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
let editingQuick = false;
let selectedClass = 0;
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
  if (editingQuick && [...document.querySelectorAll('[data-count]')].some(input => !input.value || !input.checkValidity())) {
    throw new Error('Preencha todas as quantidades com números entre 0 e 1 milhão. Zero é permitido.');
  }
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
  $('view-status').setAttribute('aria-live', 'polite');
}
function controlsEnabled(enabled) {
  for (const id of ['play', 'restart', 'advance', 'target', 'time', 'share-process', 'download-process', 'inspect-class']) $(id).disabled = !enabled;
  $('process-results').classList.toggle('is-invalid', !enabled);
  document.querySelectorAll('input[name=mechanism]').forEach(input => { input.disabled = !enabled; });
}
function fail(error) {
  stop();
  valid = false;
  $('input-error').textContent = error.message;
  $('input-error').hidden = false;
  controlsEnabled(false);
  $('view-status').textContent = 'Entrada inválida. Os gráficos abaixo ainda mostram o último cenário válido.';
  $('edit-status').textContent = 'Corrija a entrada e aplique novamente.';
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
    buildEditor();
    $('edit-status').textContent = 'Quantidades aplicadas. Altere uma classe para explorar outro início.';
    $('guide-status').textContent = 'Cenário preparado. Execute a regra ou abra a prévia do equilíbrio.';
    render();
  } catch (error) { fail(error); }
}
function markPending(source) {
  stop(); pending = true; editingQuick = source === 'quick';
  $('preset').value = 'custom';
  controlsEnabled(false);
  $('edit-status').textContent = 'Alterações pendentes. Clique em Aplicar minhas quantidades.';
  $('utility-status').textContent = 'A edição ainda não foi aplicada ao cenário.';
  $('view-status').textContent = 'Edição pendente. Os gráficos abaixo ainda mostram o cenário anterior.';
}
function buildEditor() {
  editingQuick = false;
  $('class-inputs').innerHTML = experiment.classes.map((entry, i) => `<label class="class-input" for="class-count-${i}"><span>Classe ${i + 1}<small>tamanho ${number(entry.lo)}–${number(entry.hi)}<br>${number(entry.cost)} de recurso por objeto</small></span><input id="class-count-${i}" data-count="${i}" aria-label="Quantidade inicial na classe ${i + 1}" type="number" min="0" max="1000000" step="any" required value="${experiment.initialCounts[i]}"></label>`).join('');
  selectedClass = Math.min(selectedClass, experiment.classes.length - 1);
  $('inspect-class').innerHTML = experiment.classes.map((entry, i) => `<option value="${i}">${i + 1} · tamanho ${number(entry.lo)}–${number(entry.hi)}</option>`).join('');
  $('inspect-class').value = String(selectedClass);
}
function inspectClass() {
  if (!valid || pending) return;
  const i = selectedClass;
  const entry = experiment.classes[i];
  $('inspect-description').textContent = `Cada objeto desta classe contém ${number(entry.cost)} unidades de recurso. Esse custo fica fixo durante toda a evolução.`;
  const counts = [experiment.initialCounts[i], state.counts[i], experiment.targetCounts[i]];
  const resources = [experiment.initialResources[i], state.resources[i], experiment.targetResources[i]];
  const populationTotals = [total(experiment.initialCounts), total(state.counts), total(experiment.targetCounts)];
  const rows = [
    ['Objetos equivalentes', counts.map(number)],
    ['Recurso da classe', resources.map(number)],
    ['Cota atendida', resources.map(value => percent(value / entry.targetResource))],
    ['Parcela do recurso total', resources.map(value => percent(value / experiment.budget))],
    ['Parcela de todos os objetos', counts.map((value, j) => percent(value / populationTotals[j]))],
  ];
  $('inspect-body').innerHTML = rows.map(([label, values]) => `<tr><th scope="row">${label}</th>${values.map(value => `<td>${value}</td>`).join('')}</tr>`).join('');
  $('inspect-equation').textContent = `Agora: ${number(state.counts[i])} objetos × ${number(entry.cost)} de recurso por objeto = ${number(state.resources[i])} unidades na classe. Valores arredondados para exibição.`;
}
function loadGuide(name, scroll = true) {
  stop(); editingQuick = false;
  $('measure').value = name === 'measure' ? 'linear' : 'log';
  $('exponent').value = '1'; $('max-size').value = '64'; $('counts').value = '30 30 30';
  $('preset').value = 'uniform'; $('seed').value = '42'; $('count-scale').value = 'linear';
  $('resource-view').value = 'quota'; $('advanced-controls').open = false; $('seed-row').open = false;
  document.querySelector(`input[name=mechanism][value=${name === 'random' ? 'stochastic' : 'relaxation'}]`).checked = true;
  $('time').value = name === 'random' ? '40' : '0'; viewingTarget = false; selectedClass = 0;
  apply({ reset: false });
  const hints = {
    basic: 'Exemplo A: 30 objetos em cada classe, com custos 2, 8 e 32. Execute: a cota log-orthopolic é de 420 unidades por classe.',
    measure: 'Exemplo B: mudamos apenas a medida para linear-orthopolic. As cotas são 60, 240 e 960: esta distribuição já está no alvo. Compare com o exemplo A.',
    random: 'Exemplo C: partilha aleatória com flutuações persistentes. Compare as barras verdes com os pontos roxos e use Outra realização para trocar os sorteios.',
  };
  $('guide-status').textContent = hints[name];
  if (scroll) {
    $('process-results').scrollIntoView({ block: 'start', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
    $('play').focus({ preventScroll: true });
  }
}
function drawChart(id, initial, current, target, expected, { logarithmic = false, percentage = false, label }) {
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
    const tickLabel = percentage && Math.abs(yy - y(100)) < 12 ? '' : `<text x="${left - 9}" y="${yy + 3}" text-anchor="end">${number(value)}${percentage ? '%' : ''}</text>`;
    out.push(`<line class="chart-grid" x1="${left}" y1="${yy}" x2="${width - right}" y2="${yy}"/>${tickLabel}`);
  }
  current.forEach((value, i) => {
    const x = left + groupWidth * (i + 0.5);
    const desc = `Classe ${i + 1} (tamanho ${number(experiment.classes[i].lo)} a ${number(experiment.classes[i].hi)}): inicial ${number(initial[i])}; atual ${number(value)}; alvo ${number(target[i])}${expected ? `; média ${number(expected[i])}` : ''}`;
    out.push(`<g><title>${desc}</title><rect class="initial-bar" x="${x - barWidth - 1}" y="${y(initial[i])}" width="${barWidth}" height="${Math.max(0, y(0) - y(initial[i]))}"/><rect class="current-bar" x="${x + 1}" y="${y(value)}" width="${barWidth}" height="${Math.max(0, y(0) - y(value))}"/><line class="target-mark" x1="${x - groupWidth * 0.4}" y1="${y(target[i])}" x2="${x + groupWidth * 0.4}" y2="${y(target[i])}"/>${expected ? `<circle class="mean-mark" cx="${x}" cy="${y(expected[i])}" r="3.4"/>` : ''}<text x="${x}" y="${height - 25}" text-anchor="middle">${n <= 6 ? `${number(experiment.classes[i].lo)}–${number(experiment.classes[i].hi)}` : i + 1}</text></g>`);
  });
  if (percentage) out.push(`<text x="${left - 9}" y="${y(100) + 3}" text-anchor="end" class="target-axis">100%</text>`);
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
    $('target').textContent = viewingTarget ? 'Voltar à evolução' : 'Prévia do equilíbrio';
    $('target').setAttribute('aria-pressed', String(viewingTarget));
    $('current-legend').textContent = viewingTarget ? 'Prévia (verde)' : 'Agora (verde)';
    $('inspect-current-heading').textContent = viewingTarget ? 'Prévia' : 'Agora';
    $('view-status').textContent = viewingTarget ? 'Prévia do equilíbrio · solução calculada diretamente, sem executar as trocas.' : time === 0 ? 'Distribuição inicial · nenhuma troca foi aplicada.' : showMean ? 'Realização aleatória · as barras são uma amostra; os pontos roxos são a média prevista.' : `Evolução calculada · tempo do modelo: ${number(time)}.`;
    $('time-help').textContent = viewingTarget ? 'Alvo analítico calculado diretamente. Não representa uma etapa simulada nem o estado final de uma realização aleatória.' : random ? `${state.events} encontros; tempo = encontros / ${experiment.classes.length} classes. Unidades do modelo; sem prazo físico calibrado.` : 'Tempo em unidades do modelo, sem correspondência com segundos. A animação acelera o avanço; as velocidades físicas dos processos não são comparáveis.';
    $('resource-budget').textContent = number(experiment.budget);
    const deviation = Math.abs(total(state.resources) - experiment.budget) / experiment.budget;
    $('budget-check').textContent = `Variação numérica: ${percent(deviation)}`;
    $('distance').textContent = percent(state.error);
    $('distance-label').textContent = showMean ? 'Falta redistribuir · amostra' : 'Falta redistribuir';
    $('object-count').textContent = number(total(state.counts));
    $('count-note').textContent = `Inicial: ${number(total(experiment.initialCounts))} · não conservada em geral`;
    const resourceView = $('resource-view').value;
    const normalize = values => values.map((value, i) => resourceView === 'quota' ? 100 * value / experiment.targetResources[i] : resourceView === 'density' ? value / experiment.classes[i].width : value);
    const headings = { quota: 'Quanto da cota cada classe recebeu?', total: 'Quanto recurso há em cada classe?', density: 'Recurso por unidade da medida' };
    $('resource-chart-title').textContent = headings[resourceView];
    $('resource-reading').textContent = resourceView === 'quota'
      ? '100% = cota daquela classe atendida. Acima: recurso excedente; abaixo: falta recurso. Não é porcentagem de todo o orçamento.'
      : resourceView === 'total' ? 'Cada barra mostra o estoque total de uma classe. Na medida linear, classes de larguras diferentes têm cotas diferentes.'
      : 'Dividimos o recurso de cada classe por seu peso de referência (R/w). O alvo iguala essa razão, mesmo quando as cotas totais são diferentes.';
    drawChart('resource-chart', normalize(experiment.initialResources), normalize(state.resources), normalize(experiment.targetResources), showMean ? normalize(state.expectedResources) : null, { label: headings[resourceView], percentage: resourceView === 'quota' });
    drawChart('count-chart', experiment.initialCounts, state.counts, experiment.targetCounts, showMean ? state.expectedCounts : null, { logarithmic: $('count-scale').value === 'log', label: 'Quantidades equivalentes de objetos por classe' });
    const captions = {
      log: 'Referência log-orthopolic: intervalos com a mesma razão de tamanhos recebem a mesma cota. Nesta grade, todas as classes têm pesos iguais.',
      linear: 'Referência linear-orthopolic: a cota é proporcional à largura do intervalo de tamanho. Classes mais largas recebem mais recurso total; o recurso por unidade de tamanho é que se iguala.',
      classes: 'Referência discreta: uma mesma cota por classe predefinida. Aqui, o resultado coincide com o log-orthopolic porque as classes têm larguras logarítmicas iguais.',
    };
    $('measure-caption').textContent = captions[experiment.measure];
    $('measure-help').textContent = {log: 'Log-orthopolic: o mesmo recurso para cada intervalo com a mesma razão de tamanhos. Nesta grade, todas as classes têm a mesma cota.', linear: 'Linear-orthopolic: o mesmo recurso por unidade de tamanho. Nesta grade, classes mais largas recebem cotas maiores.', classes: 'Discreta: o mesmo recurso por classe predefinida. Nesta grade geométrica, as cotas coincidem com as log-orthopolic.'}[experiment.measure];
    $('count-caption').textContent = `Cada barra conta objetos equivalentes, n = R/q, com q = k^${number(experiment.exponent)}. Não é densidade dN/dk.${$('count-scale').value === 'log' ? ' A transformação log(1 + n) permite exibir classes vazias.' : ''}`;
    const resourceRatio = experiment.classes.at(-1).cost / experiment.classes[0].cost;
    const observation = viewingTarget ? 'Você está vendo o alvo, não uma etapa simulada.' : time === 0 && state.error < 1e-10 ? 'Este início já atende às cotas da medida escolhida.' : time === 0 ? 'Compare os estoques iniciais com as cotas tracejadas antes de executar a redistribuição.' : state.error < 1e-6 ? 'As cotas foram atendidas com a precisão exibida.' : 'As barras verdes mostram a redistribuição em curso; o tracejado mantém o alvo visível.';
    $('process-insight').textContent = showMean
      ? `A média prevista está a ${percent(state.expectedError)} do alvo; esta realização, a ${percent(state.error)}. A flutuação não é uma falha: este modelo se equilibra na média e continua variando em cada realização.`
      : `${observation} ${experiment.exponent === 0 ? 'Com custo constante (d = 0), os objetos não diferem em recurso individual.' : `Um objeto da última classe concentra ${number(resourceRatio)}× o recurso de um objeto da primeira. No alvo, sua abundância por unidade da medida é ${number(resourceRatio)}× menor.`}`;
    inspectClass();
    $('process-table-caption').textContent = `Referência: ${experiment.measure === 'log' ? 'log-orthopolic' : experiment.measure === 'linear' ? 'linear-orthopolic' : 'discreta por classe'}. ${viewingTarget ? 'Alvo analítico.' : `Tempo ${number(time)}; ${{relaxation:'redistribuição global',diffusion:'difusão local',pairwise:'equilíbrio por pares',stochastic:'partilha aleatória'}[mechanism]}.`}`;
    $('process-table').innerHTML = experiment.classes.map((entry, i) => `<tr><th scope="row">${number(entry.lo)}–${number(entry.hi)}</th>${[entry.width, entry.cost, experiment.initialCounts[i], state.counts[i], experiment.targetCounts[i], state.resources[i], experiment.targetResources[i], state.resources[i] / entry.width].map(value => `<td>${number(value)}</td>`).join('')}${showMean ? `<td>${number(state.expectedResources[i])}</td>` : ''}</tr>`).join('');
  } catch (error) { fail(error); }
}
function setPreset(name) {
  let n = 3;
  try { n = Math.min(24, Math.max(2, parseCounts($('counts').value).length)); } catch { /* default grid */ }
  const presets = {
    uniform: () => 30,
    bell: i => Math.round(200 * Math.exp(-0.5 * ((i - (n - 1) / 2) / (n / 6)) ** 2)),
    small: i => i === 0 ? 800 : 0,
    large: i => i === n - 1 ? 800 : 0,
    irregular: i => [80, 3, 120, 0, 17, 200, 6, 45][i % 8],
  };
  if (presets[name]) { editingQuick = false; $('counts').value = Array.from({ length: n }, (_, i) => presets[name](i)).join(' '); apply(); }
}
function restore() { loadGuide('basic', false); }
function scenarioHash() {
  return new URLSearchParams({ p: '1', counts: experiment.initialCounts.join(','), d: experiment.exponent, measure: experiment.measure, max: experiment.maxSize, mechanism: selectedMechanism(), time: $('time').value, seed: $('seed').value, scale: $('count-scale').value, resourceView: $('resource-view').value, selectedClass, target: String(viewingTarget) }).toString();
}
function loadHash() {
  const hash = new URLSearchParams(location.hash.slice(1));
  // Preserve previously shared TV scenarios when the laboratory becomes home.
  if (hash.has('population') || hash.has('price') || hash.has('allocation')) {
    location.replace(`./tv.html${location.hash}`); return;
  }
  if (!hash.has('p')) { loadGuide('basic', false); return; }
  try {
    if (hash.get('p') !== '1') throw new Error('Versão desconhecida.');
    const counts = parseCounts(hash.get('counts') ?? '');
    const exponent = Number(hash.get('d'));
    const maxSize = Number(hash.get('max'));
    const seed = Number(hash.get('seed'));
    const time = Number(hash.get('time'));
    const mechanism = hash.get('mechanism');
    const resourceView = hash.get('resourceView') ?? 'quota';
    const inspection = Number(hash.get('selectedClass') ?? 0);
    if (!['quota', 'total', 'density'].includes(resourceView) || !Number.isInteger(inspection) || inspection < 0 || inspection >= counts.length) throw new Error('Visualização inválida.');
    if (!hash.has('d') || !hash.has('seed') || !hash.has('time') || exponent % 0.25 !== 0 || maxSize < 2 || !['linear', 'log'].includes(hash.get('scale')) || !['true', 'false'].includes(hash.get('target'))) throw new Error('Parâmetros inválidos.');
    const candidate = createExperiment({ counts, exponent, maxSize, measure: hash.get('measure') });
    evolve(candidate, { mechanism, time, seed });
    editingQuick = false;
    $('resource-view').value = resourceView; selectedClass = inspection;
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
$('counts').addEventListener('input', () => markPending('bulk'));
$('class-inputs').addEventListener('input', () => {
  const inputs = [...document.querySelectorAll('[data-count]')];
  if (inputs.every(input => input.value && input.checkValidity())) $('counts').value = inputs.map(input => input.value).join(' ');
  markPending('quick');
});
document.querySelectorAll('[data-guide]').forEach(button => button.addEventListener('click', () => loadGuide(button.dataset.guide)));
$('inspect-class').addEventListener('change', () => { selectedClass = Number($('inspect-class').value); inspectClass(); });
$('resource-view').addEventListener('change', render);
for (const id of ['measure', 'max-size']) $(id).addEventListener('change', () => apply());
$('exponent').addEventListener('input', () => apply());
document.querySelectorAll('input[name="mechanism"]').forEach(input => input.addEventListener('change', () => { stop(); viewingTarget = false; $('time').value = '0'; $('guide-status').textContent = 'Regra alterada. Mantivemos o mesmo início e orçamento; a evolução voltou ao tempo zero.'; render(); }));
$('count-scale').addEventListener('change', render);
$('time').addEventListener('input', () => { stop(); viewingTarget = false; render(); });
$('advance').addEventListener('click', () => { stop(); viewingTarget = false; $('time').value = String(Math.min(200, Number($('time').value) + 1)); render(); });
$('restart').addEventListener('click', () => { stop(); viewingTarget = false; $('time').value = '0'; render(); });
$('target').addEventListener('click', () => { stop(); viewingTarget = !viewingTarget; render(); });
$('seed').addEventListener('change', () => apply({ reset: false }));
$('new-seed').addEventListener('click', () => { $('seed').value = String(crypto.getRandomValues(new Uint32Array(1))[0]); apply({ reset: false }); });
$('play').addEventListener('click', () => {
  if (timer) { stop(); render(); return; }
  if (!valid || pending) return;
  viewingTarget = false;
  if (Number($('time').value) >= 200) $('time').value = '0';
  $('view-status').setAttribute('aria-live', 'off');
  $('play').textContent = 'Ⅱ Pausar'; $('play').setAttribute('aria-label', 'Pausar o processo');
  timer = setInterval(() => {
    const current = Number($('time').value);
    $('time').value = String(Math.min(200, current + (current < 8 ? 0.25 : current < 40 ? 1 : 4)));
    render();
    if (Number($('time').value) >= 200) { stop(); render(); }
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
