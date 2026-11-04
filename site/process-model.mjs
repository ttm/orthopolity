/**
 * Constructed resource-allocation mechanisms, not empirical evidence.
 * Classes have fixed representative costs q_j=k_j^d and reference widths w_j.
 * Every mechanism conserves B=sum(q_j N_j). Equivalent counts N_j can be
 * fractional and their sum is NOT conserved. The target is B*w_j/sum(w).
 * Reference measure: log-orthopolic, linear-orthopolic, or predefined classes.
 */

const sum = values => values.reduce((total, value) => total + value, 0);
function requireCondition(condition, message) {
  if (!condition) throw new RangeError(message);
}

/** Geometric bins; costs are specified at their geometric centers. */
export function createExperiment({
  counts = [100, 80, 60, 40, 20, 10, 5, 2],
  exponent = 1,
  measure = 'log',
  minSize = 1,
  maxSize = 64,
} = {}) {
  requireCondition(Array.isArray(counts) && counts.length >= 2 && counts.length <= 24,
    'Forneça entre 2 e 24 quantidades, uma por classe.');
  requireCondition(counts.every(value => Number.isFinite(value) && value >= 0 && value <= 1e12),
    'Cada quantidade deve estar entre 0 e 10¹² e ser finita.');
  requireCondition(Number.isFinite(exponent) && exponent >= 0 && exponent <= 3,
    'O expoente do recurso deve estar entre 0 e 3.');
  requireCondition(['log', 'linear', 'classes'].includes(measure),
    'Escolha a medida logarítmica, linear ou por classes.');
  requireCondition(Number.isFinite(minSize) && Number.isFinite(maxSize)
    && minSize >= 0.001 && maxSize <= 10000 && maxSize > minSize,
  'Os limites devem satisfazer 0,001 ≤ mínimo < máximo ≤ 10.000.');
  const length = counts.length;
  const span = Math.log(maxSize / minSize);
  const edges = Array.from({ length: length + 1 }, (_, i) => minSize * Math.exp(span * i / length));
  edges[0] = minSize;
  edges[length] = maxSize;
  const widths = counts.map((_, i) => measure === 'log' ? span / length
    : measure === 'linear' ? edges[i + 1] - edges[i] : 1);
  requireCondition(widths.every(width => Number.isFinite(width) && width > 0),
    'Os limites estão próximos demais para distinguir todas as classes.');
  const totalWidth = sum(widths);
  const weights = widths.map(width => width / totalWidth);
  const sizes = counts.map((_, i) => Math.sqrt(edges[i] * edges[i + 1]));
  const costs = sizes.map(size => size ** exponent);
  const initialResources = counts.map((count, i) => count * costs[i]);
  const budget = sum(initialResources);
  requireCondition(Number.isFinite(budget) && budget > 0,
    'A distribuição precisa conter recurso positivo; todas as quantidades não podem ser zero.');
  const targetResources = weights.map(weight => budget * weight);
  const targetCounts = targetResources.map((resource, i) => resource / costs[i]);
  requireCondition(targetCounts.every(Number.isFinite), 'Os valores excedem a precisão numérica.');
  return {
    exponent, measure, minSize, maxSize, budget, totalWidth, weights,
    initialCounts: [...counts], initialResources, targetResources, targetCounts,
    classes: counts.map((_, i) => ({
      index: i, lo: edges[i], hi: edges[i + 1], size: sizes[i],
      cost: costs[i], width: widths[i],
      targetResource: targetResources[i], targetCount: targetCounts[i],
    })),
  };
}

/** Total-variation distance between current and target resource shares, in [0,1]. */
export function resourceError(resources, experiment) {
  return 0.5 * sum(resources.map((resource, i) => Math.abs(resource / experiment.budget - experiment.weights[i])));
}

function identity(length) {
  return Array.from({ length }, (_, i) => Array.from({ length }, (_, j) => Number(i === j)));
}

function multiply(a, b) {
  const n = a.length;
  const output = Array.from({ length: n }, () => Array(n).fill(0));
  for (let i = 0; i < n; i += 1) {
    for (let k = 0; k < n; k += 1) {
      const value = a[i][k];
      for (let j = 0; j < n; j += 1) output[i][j] += value * b[k][j];
    }
  }
  return output;
}

function apply(matrix, values) {
  return matrix.map(row => sum(row.map((value, i) => value * values[i])));
}

// Repair roundoff in stochastic columns; no negative terms or clipping are used.
function normalizeColumns(matrix) {
  for (let j = 0; j < matrix.length; j += 1) {
    const total = sum(matrix.map(row => row[j]));
    for (const row of matrix) row[j] /= total;
  }
  return matrix;
}

/**
 * Neighbor diffusion: dR_i/dt=sum_j g_ij(R_j/w_j-R_i/w_i).
 * Only adjacent classes communicate. w are normalized reference widths and
 * g_ij=((K-1)^2/8)*w_i*w_j/(w_i+w_j). The K factor fixes the model clock
 * as the grid is refined; it has no empirically calibrated time unit.
 * Uniformization at a short time, followed by matrix squaring, evaluates the
 * exponential with nonnegative stochastic matrices (Poisson tail < 2e-18).
 */
function diffuse(initial, weights, time) {
  if (time === 0) return [...initial];
  const n = weights.length;
  const rates = Array.from({ length: n }, () => Array(n).fill(0));
  const leaving = Array(n).fill(0);
  const scale = (n - 1) ** 2 / 8;
  for (let i = 0; i < n - 1; i += 1) {
    const j = i + 1;
    rates[j][i] = scale * weights[j] / (weights[i] + weights[j]);
    rates[i][j] = scale * weights[i] / (weights[i] + weights[j]);
    leaving[i] += rates[j][i];
    leaving[j] += rates[i][j];
  }
  const rate = Math.max(...leaving);
  const squarings = Math.max(0, Math.ceil(Math.log2(rate * time)));
  const z = rate * time / 2 ** squarings;
  const p = rates.map((row, i) => row.map((value, j) => i === j ? 1 - leaving[i] / rate : value / rate));
  let power = identity(n);
  let poisson = Math.exp(-z);
  let transition = power.map(row => row.map(value => value * poisson));
  for (let k = 1; k <= 20; k += 1) {
    power = multiply(p, power);
    poisson *= z / k;
    for (let i = 0; i < n; i += 1) {
      for (let j = 0; j < n; j += 1) transition[i][j] += poisson * power[i][j];
    }
  }
  normalizeColumns(transition);
  for (let i = 0; i < squarings; i += 1) transition = normalizeColumns(multiply(transition, transition));
  return apply(transition, initial);
}

// Mulberry32 with open-interval output, so logarithms and gamma draws are finite.
function randomGenerator(seed) {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6D2B79F5) >>> 0;
    let value = state;
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return (((value ^ (value >>> 14)) >>> 0) + 0.5) / 4294967296;
  };
}

// Marsaglia–Tsang gamma rejection sampler in log coordinates. The logarithmic
// representation avoids underflow for small Dirichlet shape parameters.
function logGamma(shape, random) {
  if (shape < 1) return logGamma(shape + 1, random) + Math.log(random()) / shape;
  const d = shape - 1 / 3;
  const c = 1 / Math.sqrt(9 * d);
  for (;;) {
    const normal = Math.sqrt(-2 * Math.log(random())) * Math.cos(2 * Math.PI * random());
    const base = 1 + c * normal;
    if (base <= 0) continue;
    const v = base ** 3;
    const u = random();
    if (u < 1 - 0.0331 * normal ** 4 || Math.log(u) < 0.5 * normal ** 2 + d * (1 - v + Math.log(v))) {
      return Math.log(d) + Math.log(v);
    }
  }
}

function beta(a, b, random) {
  const difference = logGamma(b, random) - logGamma(a, random);
  if (difference >= 0) {
    const small = Math.exp(-difference);
    return small / (1 + small);
  }
  return 1 / (1 + Math.exp(difference));
}

function pairwise(initial, weights, events, seed, stochastic) {
  const state = [...initial];
  const random = randomGenerator(seed);
  const n = state.length;
  for (let event = 0; event < events; event += 1) {
    const i = Math.floor(random() * n);
    let j = Math.floor(random() * (n - 1));
    if (j >= i) j += 1;
    const pool = state[i] + state[j];
    const fraction = stochastic ? beta(n * weights[i], n * weights[j], random)
      : weights[i] / (weights[i] + weights[j]);
    state[i] = pool * fraction;
    state[j] = pool - state[i];
  }
  return state;
}

/** Exact ensemble mean after uniformly random pair meetings. */
function pairExpectation(initial, weights, events) {
  const n = initial.length;
  const pairs = n * (n - 1) / 2;
  let transition = identity(n);
  for (let i = 0; i < n - 1; i += 1) {
    for (let j = i + 1; j < n; j += 1) {
      const iToJ = weights[j] / (weights[i] + weights[j]) / pairs;
      const jToI = weights[i] / (weights[i] + weights[j]) / pairs;
      transition[j][i] += iToJ;
      transition[i][i] -= iToJ;
      transition[i][j] += jToI;
      transition[j][j] -= jToI;
    }
  }
  let remaining = events;
  let state = [...initial];
  while (remaining > 0) {
    if (remaining % 2 === 1) state = apply(transition, state);
    remaining = Math.floor(remaining / 2);
    if (remaining > 0) transition = normalizeColumns(multiply(transition, transition));
  }
  return state;
}

/**
 * All states are computed from the original input so slider order is irrelevant.
 * relaxation: dR/dt=R*-R; diffusion: neighbor resource-density exchange.
 * pairwise: random pair, deterministic proportional split; each path converges
 * almost surely. stochastic: random pair, beta split; only ensemble expectation
 * converges. Its invariant resource shares are Dirichlet(K*w/sum(w)); snapshots
 * retain positive variance. Time for pair mechanisms is events/K, rounded down.
 */
export function evolve(experiment, { mechanism = 'relaxation', time = 0, seed = 42 } = {}) {
  requireCondition(['relaxation', 'diffusion', 'pairwise', 'stochastic'].includes(mechanism),
    'Escolha um mecanismo válido.');
  requireCondition(Number.isFinite(time) && time >= 0 && time <= 200,
    'O tempo deve estar entre 0 e 200.');
  requireCondition(Number.isSafeInteger(seed) && seed >= 0 && seed <= 4294967295,
    'A semente deve ser um inteiro entre 0 e 4.294.967.295.');
  const { budget, weights, initialResources, targetResources, classes } = experiment;
  const initial = initialResources.map(resource => resource / budget);
  let shares;
  let expected;
  let events = 0;
  if (mechanism === 'relaxation') {
    const remainder = Math.exp(-time);
    shares = initial.map((value, i) => value * remainder + weights[i] * (1 - remainder));
  } else if (mechanism === 'diffusion') {
    shares = diffuse(initial, weights, time);
  } else {
    events = Math.floor(time * classes.length);
    shares = pairwise(initial, weights, events, seed, mechanism === 'stochastic');
    if (mechanism === 'stochastic') expected = pairExpectation(initial, weights, events);
  }
  const resources = shares.map(value => value * budget);
  const expectedResources = (expected ?? shares).map(value => value * budget);
  return {
    mechanism, time, events, seed, resources,
    counts: resources.map((resource, i) => resource / classes[i].cost),
    expectedResources,
    expectedCounts: expectedResources.map((resource, i) => resource / classes[i].cost),
    error: resourceError(resources, experiment),
    expectedError: resourceError(expectedResources, experiment),
    targetResources: [...targetResources],
  };
}
