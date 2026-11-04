import { createExperiment, evolve } from './process-model.mjs';

const $ = id => document.getElementById(id);
const total = values => values.reduce((a, b) => a + b, 0);
const number = value => Math.abs(value) >= 1e8 || (Math.abs(value) > 0 && Math.abs(value) < 0.001)
  ? value.toExponential(2).replace('.', ',')
  : new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 3 }).format(value);
const percent = value => value > 0 && value < 0.000001 ? '< 0,0001%' : `${new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 4 }).format(100 * value)}%`;
const mechanisms = {
  relaxation: ['Cada classe se aproxima de sua parcela do orçamento. A redistribuição é global e o desvio diminui exponencialmente.', 'Rⱼ(t) = Rⱼ* + [Rⱼ(0) − Rⱼ*] exp(−t)'],
  diffusion: ['Somente classes vizinhas trocam recurso. O fluxo reduz diferenças de R/w; a cadeia conectada conduz ao mesmo equilíbrio.', 'dRᵢ/dt = Σⱼ gᵢⱼ (Rⱼ/wⱼ − Rᵢ/wᵢ), com gᵢⱼ = gⱼᵢ ≥ 0'],
  pairwise: ['Um par de classes é sorteado e divide seu recurso conforme os pesos. A ordem é aleatória; cada encontro equilibra o par. A trajetória converge com encontros repetidos.', 'S = Rᵢ + Rⱼ; Rᵢ′ = S wᵢ/(wᵢ + wⱼ); Rⱼ′ = S − Rᵢ′'],
  stochastic: ['Um par de reservatórios de classe é sorteado e sua divisão também é aleatória. A média prevista converge, mas uma realização continua flutuando. Os pares são classes, não pessoas.', 'Rᵢ′ = U(Rᵢ + Rⱼ), U ~ Beta(Kwᵢ/W, Kwⱼ/W); W = Σw'],
};
let experiment;
let state;
let timer;
let viewingTarget = false;
let valid = false;
let pending = false;
const selectedMechanism = () => document.querySelector('input[name="mechanism"]:checked').value;

function parseCounts(text) {
  const tokens = text.trim().split(/[\s,;]+/);
  if (!text.trim() || tokens.some(value => !/^(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(value))) {
    throw new Error('Use números não negativos, separados por espaços, vírgulas ou ponto e vírgula; ponto para decimais.');
  }
  const values = tokens.map(Number);
  if (values.some(value => !Number.isFinite(value) || value > 1e6)) throw new Error('Cada quantidade deve ser finita e não exceder 1 milhão.');
  return values;
}
function readExperiment() {
  if (!$('max-size').value || !$('max-size').checkValidity()) throw new Error('O limite máximo deve estar entre 2 e 10.000.');
  return createExperiment({ counts: parseCounts($('counts').value), exponent: Number($('exponent').value), measure: $('measure').value, maxSize: Number($('max-size').value) });
}
function readSeed() {
  if (!$('seed').value || !$('seed').checkValidity()) throw new Error('A semente deve ser um inteiro entre 0 e 4.294.967.295.');
  return Number($('seed').value);
}
function stop() {
  clearInterval(timer);
  timer = null;
  $('play').textContent = '▶ Executar';
  $('play').setAttribute('aria-label', 'Animar o processo');
}
function controlsEnabled(enabled) {
  for (const id of ['play', 'restart', 'target', 'time', 'share-process', 'download-process']) $(id).disabled = !enabled;
  $('process-results').classList.toggle('is-invalid', !enabled);
}
function fail(error) {
  stop();
  valid = false;
  $('input-error').textContent = error.message;
  $('input-error').hidden = false;
  controlsEnabled(false);
}
function apply({ reset = true } = {}) {
  stop();
  try {
    experiment = readExperiment();
    readSeed();
    if (reset) { $('time').value = '0'; viewingTarget = false; }
    pending = false;
    valid = true;
    $('input-error').hidden = true;
    $('utility-status').textContent = '';
    controlsEnabled(true);
    render();
  } catch (error) { fail(error); }
}
function drawChart(id, initial, current, target, expected, { logarithmic = false, label }) {
  const transform = logarithmic ? value => Math.log10(1 + value) : value => value;
  const n = current.length;
  const width = Math.max(260, Math.min(720, $(id).getBoundingClientRect().width));
  const height = 212, left = 60, right = 12, top = 14, bottom = 42;
  const plotHeight = height - top - bottom;
  const plotWidth = width - left - right;
  const ymax = Math.max(...initial, ...current, ...target, ...(expected ?? []));
  const limit = transform(ymax) * 1.12 || 1;
  const y = value => top + plotHeight * (1 - transform(value) / limit);
  const groupWidth = plotWidth / n;
  const barWidth = Math.min(23, groupWidth * 0.28);
  const out = [`<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${label}. Valores completos na tabela abaixo."><title>${label}</title>`];
  for (let tick = 0; tick <= 4; tick += 1) {
    const scaled = limit * tick / 4;
    const value = logarithmic ? 10 ** scaled - 1 : scaled;
    const yy = top + plotHeight * (1 - tick / 4);
    out.push(`<line class="chart-grid" x1="${left}" y1="${yy}" x2="${width - right}" y2="${yy}"/><text x="${left - 9}" y="${yy + 3}" text-anchor="end">${number(value)}</text>`);
  }
  current.forEach((value, i) => {
    const x = left + groupWidth * (i + 0.5);
    const desc = `Classe ${i + 1}: inicial ${number(initial[i])}; atual ${number(value)}; alvo ${number(target[i])}${expected ? `; média ${number(expected[i])}` : ''}`;
    out.push(`<g><title>${desc}</title><rect class="initial-bar" x="${x - barWidth - 1}" y="${y(initial[i])}" width="${barWidth}" height="${Math.max(0, y(0) - y(initial[i]))}"/><rect class="current-bar" x="${x + 1}" y="${y(value)}" width="${barWidth}" height="${Math.max(0, y(0) - y(value))}"/><line class="target-mark" x1="${x - groupWidth * 0.4}" y1="${y(target[i])}" x2="${x + groupWidth * 0.4}" y2="${y(target[i])}"/>${expected ? `<circle class="mean-mark" cx="${x}" cy="${y(expected[i])}" r="3.4"/>` : ''}<text x="${x}" y="${height - 25}" text-anchor="middle">${i + 1}</text></g>`);
  });
  out.push(`<text class="axis-title" x="${left + plotWidth / 2}" y="${height - 5}" text-anchor="middle">Classes · k de 1 a ${number(experiment.maxSize)}</text></svg>`);
  $(id).innerHTML = out.join('');
}
function render() {
  if (!valid || pending) return;
  try {
    const mechanism = selectedMechanism();
    const time = Number($('time').value);
    state = evolve(experiment, { mechanism, time, seed: readSeed() });
    if (viewingTarget) state = { ...state, resources: [...experiment.targetResources], counts: [...experiment.targetCounts], expectedResources: [...experiment.targetResources], expectedCounts: [...experiment.targetCounts], error: 0, expectedError: 0 };
    const random = ['pairwise', 'stochastic'].includes(mechanism);
    const showMean = mechanism === 'stochastic' && !viewingTarget;
    $('seed-row').hidden = !random;
    document.querySelectorAll('.mean-legend').forEach(element => { element.hidden = !showMean; });
    $('mean-header').hidden = !showMean;
    $('mechanism-description').textContent = mechanisms[mechanism][0];
    $('mechanism-formula').textContent = mechanisms[mechanism][1];
    $('exponent-value').textContent = `d = ${number(experiment.exponent)}`;
    $('time-value').textContent = viewingTarget ? 'Alvo' : number(time);
    $('target').textContent = viewingTarget ? 'Voltar à evolução' : 'Ver alvo';
    $('time-help').textContent = viewingTarget ? 'Alvo analítico calculado diretamente. Não representa uma etapa simulada nem o estado final de uma realização aleatória.' : random ? `${state.events} encontros; tempo = encontros / ${experiment.classes.length} classes. Unidades do modelo; sem prazo físico calibrado.` : 'Tempo do modelo em unidades arbitrárias. As velocidades não são comparáveis entre mecanismos.';
    $('resource-budget').textContent = number(experiment.budget);
    const deviation = Math.abs(total(state.resources) - experiment.budget) / experiment.budget;
    $('budget-check').textContent = `Variação numérica: ${percent(deviation)}`;
    $('distance').textContent = percent(state.error);
    $('distance-label').textContent = showMean ? 'Distância desta realização' : 'Distância ao alvo';
    $('object-count').textContent = number(total(state.counts));
    $('count-note').textContent = `Inicial: ${number(total(experiment.initialCounts))} · não conservada em geral`;
    const normalized = values => values.map((value, i) => value / experiment.classes[i].width);
    drawChart('resource-chart', normalized(experiment.initialResources), normalized(state.resources), normalized(experiment.targetResources), showMean ? normalized(state.expectedResources) : null, { label: 'Recurso por unidade da medida de referência' });
    drawChart('count-chart', experiment.initialCounts, state.counts, experiment.targetCounts, showMean ? state.expectedCounts : null, { logarithmic: $('count-scale').value === 'log', label: 'Quantidades equivalentes de objetos por classe' });
    const captions = {
      log: 'Referência log-orthopolic em tamanho: R / ln(k alto / k baixo). As classes geométricas têm pesos iguais; o alvo também iguala seus estoques totais.',
      linear: 'Referência linear-orthopolic em tamanho: R / (k alto − k baixo). Classes maiores são mais largas e recebem mais recurso total; a densidade de recurso é que se iguala.',
      classes: 'Referência discreta por classe predefinida: w = 1. Nesta grade geométrica, seu perfil coincide com o log-orthopolic; os valores de R/w têm unidades distintas.',
    };
    $('measure-caption').textContent = captions[experiment.measure];
    $('count-caption').textContent = `Cada barra conta objetos equivalentes, n = R/q, com q = k^${number(experiment.exponent)}. Não é densidade dN/dk.${$('count-scale').value === 'log' ? ' A transformação log(1 + n) permite exibir classes vazias.' : ''}`;
    const resourceRatio = experiment.classes.at(-1).cost / experiment.classes[0].cost;
    $('process-insight').textContent = showMean
      ? `A média prevista está a ${percent(state.expectedError)} do alvo; esta realização, a ${percent(state.error)}. Os pontos roxos são a média matemática de muitas realizações possíveis, não uma média temporal desta amostra. Flutuações persistem no equilíbrio.`
      : `${viewingTarget ? 'No alvo analítico' : 'Ao atingir o alvo'}, a abundância por unidade da medida, n/w, é inversamente proporcional ao recurso por objeto. ${experiment.exponent === 0 ? 'Com d = 0, todos os objetos têm o mesmo recurso: este cenário não produz diferença individual de q.' : `Os objetos da última classe concentram ${number(resourceRatio)}× o recurso dos da primeira; sua abundância por unidade da medida é ${number(resourceRatio)}× menor.`} A distância exibida mede alocação entre classes, não desigualdade entre pessoas.`;
    $('process-table-caption').textContent = `Referência: ${experiment.measure === 'log' ? 'log-orthopolic' : experiment.measure === 'linear' ? 'linear-orthopolic' : 'discreta por classe'}. ${viewingTarget ? 'Alvo analítico.' : `Tempo ${number(time)}; ${mechanism}.`}`;
    $('process-table').innerHTML = experiment.classes.map((entry, i) => `<tr><th scope="row">${number(entry.lo)}–${number(entry.hi)}</th>${[entry.width, entry.cost, experiment.initialCounts[i], state.counts[i], experiment.targetCounts[i], state.resources[i], experiment.targetResources[i], state.resources[i] / entry.width].map(value => `<td>${number(value)}</td>`).join('')}${showMean ? `<td>${number(state.expectedResources[i])}</td>` : ''}</tr>`).join('');
  } catch (error) { fail(error); }
}
function setPreset(name) {
  let n = 8;
  try { n = Math.min(24, Math.max(2, parseCounts($('counts').value).length)); } catch { /* default grid */ }
  const presets = {
    uniform: () => 100,
    bell: i => Math.round(200 * Math.exp(-0.5 * ((i - (n - 1) / 2) / (n / 6)) ** 2)),
    small: i => i === 0 ? 800 : 0,
    large: i => i === n - 1 ? 800 : 0,
    irregular: i => [80, 3, 120, 0, 17, 200, 6, 45][i % 8],
  };
  if (presets[name]) { $('counts').value = Array.from({ length: n }, (_, i) => presets[name](i)).join(' '); apply(); }
}
function restore() {
  $('measure').value = 'log'; $('exponent').value = '1'; $('max-size').value = '64';
  $('counts').value = '100 100 100 100 100 100 100 100'; $('preset').value = 'uniform';
  $('seed').value = '42'; $('count-scale').value = 'linear';
  document.querySelector('input[value="relaxation"]').checked = true;
  apply();
}
function scenarioHash() {
  return new URLSearchParams({ p: '1', counts: experiment.initialCounts.join(','), d: experiment.exponent, measure: experiment.measure, max: experiment.maxSize, mechanism: selectedMechanism(), time: $('time').value, seed: $('seed').value, scale: $('count-scale').value, target: String(viewingTarget) }).toString();
}
function loadHash() {
  const hash = new URLSearchParams(location.hash.slice(1));
  // Preserve previously shared TV scenarios when the laboratory becomes home.
  if (hash.has('population') || hash.has('price') || hash.has('allocation')) {
    location.replace(`./tv.html${location.hash}`); return;
  }
  if (!hash.has('p')) { apply(); return; }
  try {
    if (hash.get('p') !== '1') throw new Error('Versão desconhecida.');
    const counts = parseCounts(hash.get('counts') ?? '');
    const exponent = Number(hash.get('d'));
    const maxSize = Number(hash.get('max'));
    const seed = Number(hash.get('seed'));
    const time = Number(hash.get('time'));
    const mechanism = hash.get('mechanism');
    if (!hash.has('d') || !hash.has('seed') || !hash.has('time') || exponent % 0.25 !== 0 || maxSize < 2 || !['linear', 'log'].includes(hash.get('scale')) || !['true', 'false'].includes(hash.get('target'))) throw new Error('Parâmetros inválidos.');
    const candidate = createExperiment({ counts, exponent, maxSize, measure: hash.get('measure') });
    evolve(candidate, { mechanism, time, seed });
    $('counts').value = counts.join(' '); $('exponent').value = String(exponent); $('measure').value = candidate.measure; $('max-size').value = String(maxSize);
    $('seed').value = String(seed); $('time').value = String(time); $('count-scale').value = hash.get('scale'); $('preset').value = 'custom';
    document.querySelector(`input[name="mechanism"][value="${mechanism}"]`).checked = true;
    viewingTarget = hash.get('target') === 'true';
    apply({ reset: false });
  } catch { restore(); $('utility-status').textContent = 'O link contém parâmetros inválidos. O cenário padrão foi restaurado.'; }
}
$('process-parameters').addEventListener('submit', event => { event.preventDefault(); apply(); });
$('restore').addEventListener('click', restore);
$('preset').addEventListener('change', () => setPreset($('preset').value));
$('counts').addEventListener('input', () => { stop(); pending = true; $('preset').value = 'custom'; controlsEnabled(false); $('utility-status').textContent = 'Edição pendente: clique em Aplicar distribuição.'; });
for (const id of ['measure', 'max-size']) $(id).addEventListener('change', () => apply());
$('exponent').addEventListener('input', () => apply());
document.querySelectorAll('input[name="mechanism"]').forEach(input => input.addEventListener('change', () => { stop(); viewingTarget = false; $('time').value = '0'; render(); }));
$('count-scale').addEventListener('change', render);
$('time').addEventListener('input', () => { stop(); viewingTarget = false; render(); });
$('restart').addEventListener('click', () => { stop(); viewingTarget = false; $('time').value = '0'; render(); });
$('target').addEventListener('click', () => { stop(); viewingTarget = !viewingTarget; render(); });
$('seed').addEventListener('change', () => apply({ reset: false }));
$('new-seed').addEventListener('click', () => { $('seed').value = String(crypto.getRandomValues(new Uint32Array(1))[0]); apply({ reset: false }); });
$('play').addEventListener('click', () => {
  if (timer) { stop(); return; }
  if (!valid || pending) return;
  viewingTarget = false;
  if (Number($('time').value) >= 200) $('time').value = '0';
  $('play').textContent = 'Ⅱ Pausar'; $('play').setAttribute('aria-label', 'Pausar o processo');
  timer = setInterval(() => {
    const current = Number($('time').value);
    $('time').value = String(Math.min(200, current + (current < 8 ? 0.25 : current < 40 ? 1 : 4)));
    render();
    if (Number($('time').value) >= 200) stop();
  }, 120);
});
document.addEventListener('visibilitychange', () => { if (document.hidden) stop(); });
$('share-process').addEventListener('click', async () => {
  if (!valid || pending) return;
  const link = new URL(location.href); link.hash = scenarioHash();
  history.replaceState(null, '', link);
  try { await navigator.clipboard.writeText(link.href); $('utility-status').textContent = 'Link copiado. Ele preserva a distribuição, o processo e a etapa.'; }
  catch { $('utility-status').textContent = `Copie o endereço do navegador: ${link.href}`; }
});
$('download-process').addEventListener('click', () => {
  if (!valid || pending) return;
  const rows = [['measure', 'mechanism', 'view', 'time', 'seed', 'class', 'k_low', 'k_high', 'k_representative', 'reference_width', 'resource_per_object', 'initial_count', 'current_count', 'target_count', 'current_resource', 'target_resource', 'resource_per_reference_width', 'expected_resource', 'budget']];
  experiment.classes.forEach((entry, i) => rows.push([experiment.measure, selectedMechanism(), viewingTarget ? 'analytic_target' : 'evolution', $('time').value, $('seed').value, i + 1, entry.lo, entry.hi, entry.size, entry.width, entry.cost, experiment.initialCounts[i], state.counts[i], experiment.targetCounts[i], state.resources[i], experiment.targetResources[i], state.resources[i] / entry.width, state.expectedResources[i], experiment.budget]));
  const url = URL.createObjectURL(new Blob([rows.map(row => row.join(',')).join('\n') + '\n'], { type: 'text/csv;charset=utf-8' }));
  const anchor = document.createElement('a'); anchor.href = url; anchor.download = 'orthopolity-processo.csv'; document.body.append(anchor); anchor.click(); anchor.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  $('utility-status').textContent = 'CSV exportado com valores completos, medida e parâmetros do cenário.';
});
window.addEventListener('hashchange', () => {
  const hash = new URLSearchParams(location.hash.slice(1));
  if (['p', 'population', 'price', 'allocation'].some(key => hash.has(key))) loadHash();
});
let resizeTimer;
window.addEventListener('resize', () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(render, 120); });
loadHash();
