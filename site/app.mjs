import { DEFAULTS, computeModel } from './model.mjs';

const $ = id => document.getElementById(id);
const integer = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 0 });
const decimal = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 2 });
const currency = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 2 });
const compact = new Intl.NumberFormat('pt-BR', { notation: 'compact', maximumFractionDigits: 2 });
const money = value => `R$ ${compact.format(value)}`;
const full = value => currency.format(value);
let current;

function readForm() {
  return {
    population: Number($('population').value) * 1e6,
    price: Number($('price').value),
    margin: Number($('margin').value) / 100,
    owners: Number($('owners').value),
    branching: Number($('branching').value),
    allocation: document.querySelector('input[name="allocation"]:checked').value,
    tax: $('tax').checked,
  };
}

function setForm(params) {
  $('population').value = params.population / 1e6;
  $('price').value = params.price;
  $('margin').value = params.margin * 100;
  $('owners').value = params.owners;
  $('branching').value = params.branching;
  $('tax').checked = params.tax;
  document.querySelector(`input[name="allocation"][value="${params.allocation}"]`).checked = true;
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function drawPeople(model) {
  const { groups, maxBenefit, params } = model;
  const isLog = $('scale').value === 'log';
  const transform = value => isLog ? Math.log10(1 + value) : value;
  const denominator = transform(maxBenefit) || 1;
  const position = value => `${Math.min(100, Math.max(0, 100 * transform(value) / denominator))}%`;
  const chart = $('person-chart');
  chart.replaceChildren();
  groups.filter(group => group.count > 0).forEach(group => {
    const row = el('div', 'person-row');
    const label = el('div', 'person-label', group.label);
    label.append(el('small', '', `${integer.format(group.count)} ${group.count === 1 ? 'pessoa' : 'pessoas'}`));
    const track = el('div', 'track');
    const stem = el('span', 'stem');
    stem.style.width = position(group.benefit);
    const dot = el('span', 'dot');
    dot.style.left = position(group.benefit);
    track.append(stem, dot);
    if (!params.tax) {
      const base = el('span', 'tv-dot');
      base.style.left = position(params.price);
      track.append(base);
    }
    const value = el('div', 'person-value', money(group.benefit));
    value.title = full(group.benefit);
    row.append(label, track, value);
    chart.append(row);
  });
  $('chart-title').textContent = params.tax ? 'Saldo por pessoa após o imposto' : 'Valor recebido por pessoa';
  document.querySelector('.legend').hidden = params.tax;
  $('chart-caption').textContent = (isLog
    ? 'Escala log(1 + valor em R$): acomoda o zero e comprime grandes diferenças. Posição máxima: '
    : 'Escala linear, de zero até ') + `${full(maxBenefit)}. Valores arredondados; tabela com valores completos abaixo.`;
  chart.setAttribute('aria-label', groups.filter(g => g.count > 0).map(g => `${g.label}: ${full(g.benefit)} por pessoa`).join('. '));
}

function drawPools(model) {
  const chart = $('pool-chart');
  const groups = model.groups.filter(group => group.count > 0 && (group.id !== 'general' || model.params.allocation === 'people'));
  const max = Math.max(...groups.map(group => group.pool)) || 1;
  chart.replaceChildren();
  for (const group of groups) {
    const row = el('div', 'pool-row');
    const track = el('div', 'pool-track');
    const bar = el('span');
    bar.style.width = `${group.pool / max * 100}%`;
    track.append(bar);
    const value = el('span', 'pool-number', money(group.pool));
    value.title = full(group.pool);
    row.append(el('span', '', group.label), track, value);
    chart.append(row);
  }
  $('pool-caption').textContent = model.capture === 0
    ? 'Sem verba adicional, não há recebimentos positivos nem espectro logarítmico.'
    : model.params.allocation === 'levels'
      ? `Mesma verba em cada um dos cinco níveis: ${full(model.capture / 5)}. Esta é a igualdade ortopólica discreta do cenário. Barras em escala linear.`
      : model.params.allocation === 'top'
        ? 'A fábrica recebe cinco vezes a verba de cada outro nível. A igualdade ortopólica por nível deixa de valer. Barras em escala linear.'
        : 'O dividendo é igual por cidadão. Grupos maiores recebem mais no total; a igualdade por nível deixa de valer. Barras em escala linear.';
}

function drawLorenz(model) {
  const svg = $('lorenz-chart');
  const path = model.lorenz.map(({ x, y }, index) => `${index ? 'L' : 'M'} ${35 + x * 215} ${180 - y * 150}`).join(' ');
  svg.innerHTML = `<path d="M35 30V180H250" fill="none" stroke="#cbd3c7"/><path d="M35 180L250 30" stroke="#acb9ae" stroke-dasharray="4 4"/><path d="${path}" fill="none" stroke="#c46636" stroke-width="2.5"/><g fill="#67766e" font-family="sans-serif" font-size="9"><text x="18" y="184">0</text><text x="13" y="34">100</text><text x="231" y="195">100%</text><text x="35" y="209">População acumulada →</text><text x="35" y="16">Valor acumulado (%)</text></g>`;
  const zero = model.totalBenefit === 0;
  $('gini').textContent = zero ? '—' : model.gini.toLocaleString('pt-BR', { minimumFractionDigits: 3, maximumFractionDigits: 3 });
  $('gini').title = zero ? 'Indefinido: todos os saldos são zero.' : model.gini.toLocaleString('pt-BR', { maximumFractionDigits: 9 });
  if (zero) {
    svg.querySelector('path:last-of-type').setAttribute('stroke', 'none');
    $('gini-note').textContent = 'Todos os saldos são zero. Gini e curva de Lorenz não são definidos quando a soma é zero; a linha tracejada é apenas a referência de igualdade.';
  } else if (model.params.tax) {
    $('gini-note').textContent = 'Após o imposto uniforme, o aparelho e o tributo se compensam nesta conta parcial. A curva mostra somente os recebimentos adicionais. Não representa patrimônio ou bem-estar.';
  } else {
    const extraGini = computeModel({ ...model.params, tax: true }).gini;
    $('gini-note').textContent = model.capture === 0
      ? 'Todos recebem apenas a mesma TV. O valor contabilizado é igual e a curva coincide com a diagonal tracejada.'
      : `O Gini inclui a TV comum a todos. Se olharmos só o adicional, ele é ${extraGini.toLocaleString('pt-BR', { minimumFractionDigits: 6, maximumFractionDigits: 6 })}. Uma grande distância entre extremos pode coexistir com um Gini bruto baixo.`;
  }
}

function renderTable(model) {
  const body = $('table-body');
  body.replaceChildren();
  for (const group of model.groups) {
    const row = el('tr');
    const heading = el('th', '', group.label);
    heading.scope = 'row';
    row.append(heading);
    for (const value of [integer.format(group.count), full(group.pool), full(group.extra), group.count ? full(group.benefit) : '—']) row.append(el('td', '', value));
    body.append(row);
  }
  $('table-caption').textContent = `População: ${integer.format(model.params.population)}. Cada pessoa aparece uma vez e recebe uma TV de ${full(model.params.price)}.`;
  $('accounting').textContent = `Orçamento: ${full(model.budget)} = demais custos ${full(model.productionCost)} + comissões e lucros ${full(model.capture)}. * Valor por pessoa = TV + adicional${model.params.tax ? ` − imposto uniforme de ${full(model.params.price)}` : ''}. Soma desta conta parcial: ${full(model.totalBenefit)}. Essa soma combina bens e recebimentos monetários; não é dinheiro criado nem orçamento adicional. Os beneficiários dos demais custos não são individualizados.`;
}

function render() {
  $('margin-output').value = `${$('margin').value}%`;
  $('branching-output').value = `${$('branching').value}×`;
  $('utility-status').textContent = '';
  try {
    if (!$('parameters').checkValidity()) throw new RangeError('Preencha os campos com valores dentro dos limites indicados.');
    current = computeModel(readForm());
    $('error').hidden = true;
    $('results').removeAttribute('aria-busy');
    $('results').inert = false;
    document.querySelector('.secondary-grid').hidden = false;
    document.querySelector('.table-details').hidden = false;
    $('share').disabled = false;
    $('download').disabled = false;
  } catch (error) {
    current = null;
    $('error').textContent = `${error.message} Os resultados anteriores estão suspensos até a correção.`;
    $('error').hidden = false;
    $('results').setAttribute('aria-busy', 'true');
    // Keep rule controls operable: a user may be navigating them with a keyboard.
    document.querySelector('.secondary-grid').hidden = true;
    document.querySelector('.table-details').hidden = true;
    $('share').disabled = true;
    $('download').disabled = true;
    return;
  }
  const model = current;
  $('budget').textContent = money(model.budget);
  $('capture').textContent = money(model.capture);
  $('budget-note').textContent = `${compact.format(model.params.population)} de aparelhos`;
  $('capture-note').textContent = model.params.allocation === 'people' ? 'Dividendo para toda a população' : 'Divididos entre cinco níveis';
  $('ratio').textContent = model.totalBenefit === 0 ? '—' : Number.isFinite(model.ratio) ? `${integer.format(model.ratio)}×` : 'Sem razão finita';
  $('ratio-note').textContent = model.totalBenefit === 0 ? 'Todos os saldos são zero' : model.minBenefit === 0 ? 'O menor saldo é zero' : model.params.tax ? 'Saldo após imposto uniforme' : 'TV + recebimento adicional';
  const factory = model.groups.at(-1);
  $('insight').textContent = model.capture === 0
    ? 'Sem comissões e lucros selecionados, todos têm o mesmo resultado nesta conta. A desigualdade não é uma consequência necessária da entrega de TVs.'
    : model.params.allocation === 'people'
      ? `Cada cidadão recebe ${full(model.capture / model.params.population)} de dividendo, além da TV. Redistribuir a mesma verba a todos elimina as diferenças neste modelo; essa é uma regra alternativa, que exige mudar a destinação dos ganhos.`
      : `Cada dono de fábrica recebe uma TV e mais ${full(factory.extra)}. ${model.params.allocation === 'levels' ? `A verba de seu nível é igual à de todos os vendedores juntos: ${money(factory.pool)}. Menos recebedores, maior ganho individual.` : 'O topo concentra 5/9 da verba adicional. Agora a verba dos níveis também é desigual.'}`;
  drawPeople(model);
  drawPools(model);
  drawLorenz(model);
  renderTable(model);
}

function scenarioURL() {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(current.params)) params.set(key, String(value));
  params.set('scale', $('scale').value);
  return `${location.href.split('#')[0]}#${params}`;
}

function loadHash() {
  if (!location.hash.includes('=')) return;
  try {
    const hash = new URLSearchParams(location.hash.slice(1));
    const params = { ...DEFAULTS };
    for (const key of ['population', 'price', 'margin', 'owners', 'branching']) if (hash.has(key)) params[key] = Number(hash.get(key));
    if (hash.has('allocation')) params.allocation = hash.get('allocation');
    if (hash.has('tax')) {
      if (!['true', 'false'].includes(hash.get('tax'))) throw new Error('Invalid tax');
      params.tax = hash.get('tax') === 'true';
    }
    computeModel(params);
    // Shared scenarios use exactly the same limits and granularity as the form.
    if (params.population < 1e6 || params.population > 1e9 || params.population % 1e6 || params.price > 1e6 || !Number.isInteger(params.price) || params.owners > 1e6 || Math.abs(params.margin * 100 - Math.round(params.margin * 100)) > 1e-8) throw new Error('Outside form limits');
    setForm(params);
    $('scale').value = hash.get('scale') === 'linear' ? 'linear' : 'log';
    render();
  } catch {
    setForm(DEFAULTS);
    render();
    $('utility-status').textContent = 'Link com parâmetros inválidos. O cenário inicial foi restaurado.';
  }
}

$('parameters').addEventListener('submit', event => event.preventDefault());
$('parameters').addEventListener('input', render);
document.querySelectorAll('input[name="allocation"]').forEach(input => input.addEventListener('change', render));
$('scale').addEventListener('change', () => { if (current) drawPeople(current); });
$('reset').addEventListener('click', () => {
  setForm(DEFAULTS);
  $('scale').value = 'log';
  history.replaceState(null, '', location.pathname + location.search);
  render();
});
$('share').addEventListener('click', async () => {
  if (!current) return;
  const url = scenarioURL();
  history.replaceState(null, '', url);
  try {
    await navigator.clipboard.writeText(url);
    $('utility-status').textContent = 'Link copiado com os parâmetros deste cenário.';
  } catch {
    $('utility-status').textContent = 'O cenário foi salvo no endereço da página. Copie o link da barra de endereços.';
  }
});
$('download').addEventListener('click', () => {
  if (!current) return;
  const model = current;
  const rows = [
    ['Modelo hipotético de uma compra de TVs; moeda BRL; valores nominais'],
    ['regra', model.params.allocation, 'populacao', model.params.population, 'preco_tv', model.params.price, 'fracao_adicional', model.params.margin, 'fator', model.params.branching, 'donos_fabricas', model.params.owners, 'imposto_uniforme', model.params.tax],
    ['orcamento', model.budget, 'custos_demais', model.productionCost, 'comissoes_lucros', model.capture],
    ['grupo', 'pessoas', 'verba_adicional_grupo', 'adicional_pessoa', 'valor_tv', 'imposto_pessoa', 'valor_contabilizado_pessoa'],
    ...model.groups.map(g => [g.label, g.count, g.pool, g.extra, g.tvValue, g.tax, g.count ? g.benefit : '']),
  ];
  const csv = '\uFEFF' + rows.map(row => row.map(value => `"${String(typeof value === 'number' ? value.toLocaleString('pt-BR', { useGrouping: false, maximumFractionDigits: 10 }) : value).replaceAll('"', '""')}"`).join(';')).join('\r\n');
  const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
  const anchor = el('a');
  anchor.href = url;
  anchor.download = 'ortopolidade-tvs.csv';
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  $('utility-status').textContent = 'Tabela exportada com as hipóteses deste cenário.';
});
window.addEventListener('hashchange', loadHash);
render();
loadHash();
