import test from 'node:test';
import assert from 'node:assert/strict';
import { createExperiment, evolve, resourceError } from '../site/process-model.mjs';
const sum = values => values.reduce((a, b) => a + b, 0);
const near = (actual, expected, tolerance = 1e-10) => assert.ok(Math.abs(actual - expected) <= tolerance * Math.max(1, Math.abs(expected)), `${actual} != ${expected}`);
const mechanisms = ['relaxation', 'diffusion', 'pairwise', 'stochastic'];

test('inverse-resource target uses the declared measure and fixed budget', () => {
  const log = createExperiment({ counts: [3, 0, 11, 2], exponent: 2, maxSize: 16 });
  near(log.budget, 3 * 2 + 11 * 32 + 2 * 128);
  log.classes.forEach((entry, i) => { near(entry.width, Math.log(2)); near(log.targetResources[i], log.budget / 4); near(log.targetCounts[i], log.budget / 4 / entry.cost); });
  const linear = createExperiment({ counts: [3, 0, 11, 2], exponent: 2, measure: 'linear', maxSize: 16 });
  near(linear.weights[0], 1 / 15); near(linear.weights[3], 8 / 15);
  near(linear.targetResources[3] / linear.targetResources[0], 8);
  near(linear.targetCounts[0] / linear.targetCounts[3], 8);
  near(log.targetCounts[0] / log.targetCounts[3], 64);
});

test('log and discrete weights yield the same target on a geometric grid', () => {
  const log = createExperiment({ counts: [1, 0, 4, 5] });
  const discrete = createExperiment({ counts: [1, 0, 4, 5], measure: 'classes' });
  log.targetCounts.forEach((v, i) => near(v, discrete.targetCounts[i]));
  assert.notEqual(log.classes[0].width, discrete.classes[0].width);
});

test('constant cost does not create individual resource inequality', () => {
  const e = createExperiment({ counts: [1, 0, 7], exponent: 0 });
  e.classes.forEach(entry => assert.equal(entry.cost, 1));
  near(sum(e.targetCounts), sum(e.initialCounts));
});

test('resource conservation does not imply count conservation', () => {
  const e = createExperiment({ counts: [100, 0, 0], exponent: 2 });
  near(sum(e.targetResources), e.budget);
  assert.ok(Math.abs(sum(e.targetCounts) - 100) > 10);
});

for (const mechanism of mechanisms) {
  test(`${mechanism}: preserves positive resource, handles empty classes, and starts exactly at the input`, () => {
    for (const measure of ['log', 'linear', 'classes']) {
      for (const count of [2, 8, 24]) {
        const e = createExperiment({ counts: [1e6, ...Array(count - 1).fill(0)], exponent: 3, measure, maxSize: 10000 });
        const initial = evolve(e, { mechanism, time: 0 });
        initial.resources.forEach((value, i) => near(value, e.initialResources[i]));
        for (const time of [0.25, 3.5, 200]) {
          const state = evolve(e, { mechanism, time });
          assert.ok(state.resources.every(value => Number.isFinite(value) && value >= 0));
          assert.ok(state.counts.every(value => Number.isFinite(value) && value >= 0));
          near(sum(state.resources), e.budget, 2e-12);
          near(sum(state.expectedResources), e.budget, 2e-12);
          assert.ok(state.error >= 0 && state.error <= 1 + 1e-12);
          state.counts.forEach((value, i) => near(value * e.classes[i].cost, state.resources[i]));
        }
      }
    }
  });
}

test('global relaxation has the independently specified exponential distance decay', () => {
  const e = createExperiment({ counts: [1, 7, 0, 3], measure: 'linear' });
  const initialError = resourceError(e.initialResources, e);
  for (const time of [0.25, 1, 5]) near(evolve(e, { time }).error, initialError * Math.exp(-time));
});

test('two-reservoir diffusion agrees with the exact ODE solution at rate 1/8', () => {
  for (const measure of ['log', 'linear']) {
    const e = createExperiment({ counts: [10, 0], measure });
    for (const time of [0.125, 1, 10, 50]) {
      const state = evolve(e, { mechanism: 'diffusion', time });
      e.classes.forEach((entry, i) => near(state.resources[i], e.targetResources[i] + (e.initialResources[i] - e.targetResources[i]) * Math.exp(-time / 8)));
    }
  }
});

test('neighbor diffusion has the correct short-time local flux', () => {
  const e = createExperiment({ counts: [9, 0, 0], exponent: 0 });
  const s = evolve(e, { mechanism: 'diffusion', time: 1e-6 });
  // K=3: scale=(K-1)^2/8=.5, so transfer rate from 0 to 1 is .25.
  near((s.resources[1] - e.initialResources[1]) / 1e-6, 2.25, 1e-6);
  assert.ok(s.resources[2] < 1e-11);
});

test('three convergent mechanisms reach their declared target from extreme starts', () => {
  for (const measure of ['log', 'linear']) for (const count of [2, 8, 24]) {
    const e = createExperiment({ counts: [...Array(count - 1).fill(0), 800], measure, maxSize: 10000 });
    for (const mechanism of ['relaxation', 'diffusion', 'pairwise']) assert.ok(evolve(e, { mechanism, time: 200 }).error < 2e-10);
    assert.ok(evolve(e, { mechanism: 'stochastic', time: 200 }).expectedError < 2e-10);
  }
});

test('pair balancing of two classes reaches the target in exactly one encounter', () => {
  const e = createExperiment({ counts: [8, 0], measure: 'linear' });
  const state = evolve(e, { mechanism: 'pairwise', time: 0.5 });
  assert.equal(state.events, 1); near(state.error, 0);
});

test('random paths are reproducible regardless of slider history and differ by seed', () => {
  const e = createExperiment({ counts: [8, 0, 5, 1] });
  for (const mechanism of ['pairwise', 'stochastic']) {
    const options = { mechanism, time: 0.75, seed: 17 };
    const first = evolve(e, options);
    evolve(e, { ...options, time: 100 });
    assert.deepEqual(evolve(e, options), first);
    assert.notDeepEqual(evolve(e, { ...options, seed: 18 }).resources, first.resources);
  }
});

test('a uniform random two-class split has the predicted mean and persistent variance', () => {
  const e = createExperiment({ counts: [100, 0], exponent: 0 });
  const samples = Array.from({ length: 2048 }, (_, seed) => evolve(e, { mechanism: 'stochastic', time: 0.5, seed }).resources[0] / e.budget);
  const mean = sum(samples) / samples.length;
  const variance = sum(samples.map(value => (value - mean) ** 2)) / samples.length;
  near(mean, 0.5, 0.025); near(variance, 1 / 12, 0.012);
  const state = evolve(e, { mechanism: 'stochastic', time: 200 });
  assert.ok(state.error > 0.01); near(state.expectedError, 0);
});

test('unequal-width stochastic ensemble matches the exact transient mean', () => {
  const e = createExperiment({ counts: [9, 0, 1], measure: 'linear', maxSize: 8 });
  const predicted = evolve(e, { mechanism: 'stochastic', time: 1 }).expectedResources.map(x => x / e.budget);
  const observed = [0, 0, 0];
  for (let seed = 0; seed < 4096; seed++) {
    evolve(e, { mechanism: 'stochastic', time: 1, seed }).resources.forEach((value, i) => { observed[i] += value / e.budget / 4096; });
  }
  observed.forEach((value, i) => near(value, predicted[i], 0.025));
});

test('input validation rejects undefined or nonfinite distributions and controls', () => {
  for (const counts of [[0, 0], [-1, 3], [NaN, 1], [Infinity, 1], [1], Array(25).fill(1), [1e13, 1]]) assert.throws(() => createExperiment({ counts }), RangeError);
  for (const options of [{ measure: 'unknown' }, { exponent: 4 }, { exponent: NaN }, { minSize: 0 }, { maxSize: 1 }, { maxSize: Infinity }]) assert.throws(() => createExperiment(options), RangeError);
  const e = createExperiment();
  for (const options of [{ time: -1 }, { time: 201 }, { time: NaN }, { seed: 1.5 }, { seed: -1 }, { seed: 2 ** 32 }, { mechanism: 'unknown' }]) assert.throws(() => evolve(e, options), RangeError);
});
