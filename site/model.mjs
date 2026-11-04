/**
 * A synthetic, one-purchase incidence model. Money paid to the supply chain is
 * partitioned once; sales turnover at successive levels is never added together.
 * Equal level pools are discretely orthopolic. With geometric group counts they
 * are log-orthopolic on the finite grid of positive additional receipts, not on
 * total benefits (TV plus receipts), and not linear-orthopolic.
 */
export const DEFAULTS = Object.freeze({
  population: 100_000_000,
  price: 2_000,
  margin: 0.1,
  branching: 10,
  owners: 1,
  allocation: 'levels',
  tax: false,
});

const LEVELS = [
  ['sellers', 'Vendedores'],
  ['managers', 'Gerentes'],
  ['shops', 'Donos de lojas'],
  ['networks', 'Donos de redes'],
  ['factories', 'Donos de fábricas'],
];

function requireCondition(condition, message) {
  if (!condition) throw new RangeError(message);
}

/**
 * Benefits are a transparent accounting proxy, not welfare or total wealth.
 * tax=true subtracts a uniform levy equal to the TV purchase price from each
 * citizen. Other production incomes and opportunity costs are outside this model.
 */
export function computeModel(input = {}) {
  const params = { ...DEFAULTS, ...input };
  const { population, price, margin, branching, owners, allocation, tax } = params;
  requireCondition(Number.isSafeInteger(population) && population > 0,
    'A população deve ser um número inteiro positivo.');
  requireCondition(Number.isFinite(price) && price > 0,
    'O preço da TV deve ser positivo e finito.');
  requireCondition(Number.isFinite(margin) && margin >= 0 && margin <= 1,
    'A parcela de comissões e lucros deve estar entre 0 e 1.');
  requireCondition(Number.isSafeInteger(branching) && branching >= 2 && branching <= 20,
    'O fator entre níveis deve ser um inteiro entre 2 e 20.');
  requireCondition(Number.isSafeInteger(owners) && owners > 0,
    'O número de donos de fábricas deve ser um inteiro positivo.');
  requireCondition(['levels', 'people', 'top'].includes(allocation),
    'Escolha uma regra de distribuição válida.');
  requireCondition(typeof tax === 'boolean', 'O financiamento deve ser verdadeiro ou falso.');

  const counts = LEVELS.map((_, j) => owners * branching ** (4 - j));
  const chainCount = counts.reduce((sum, count) => sum + count, 0);
  requireCondition(Number.isSafeInteger(chainCount) && chainCount <= population,
    'A cadeia precisa caber na população: reduza os donos ou o fator entre níveis.');

  const budget = population * price;
  const capture = budget * margin;
  const productionCost = budget - capture;
  requireCondition(Number.isFinite(budget) && Number.isFinite(budget + capture),
    'Os valores escolhidos excedem a precisão numérica do modelo.');

  const rows = [['general', 'Demais cidadãos', population - chainCount],
    ...LEVELS.map(([id, label], j) => [id, label, counts[j]])];
  const base = tax ? 0 : price;
  const groups = rows.map(([id, label, count], index) => {
    let pool = 0;
    if (allocation === 'people') pool = capture * (count / population);
    else if (index > 0) pool = capture * (allocation === 'levels' ? 1 / 5 : (index === 5 ? 5 : 1) / 9);
    const extra = count === 0 ? 0 : pool / count;
    return { id, label, count, pool, extra, benefit: base + extra, tvValue: price, tax: tax ? price : 0 };
  });

  const occupied = groups.filter(group => group.count > 0);
  const sorted = [...occupied].sort((a, b) => a.benefit - b.benefit);
  const totalBenefit = occupied.reduce((sum, group) => sum + group.count * group.benefit, 0);
  const mean = totalBenefit / population;
  const minBenefit = sorted[0].benefit;
  const maxBenefit = sorted.at(-1).benefit;
  const ratio = minBenefit > 0 ? maxBenefit / minBenefit : maxBenefit > 0 ? Infinity : 1;

  // Pairwise grouped Gini: sum_{i<j} p_i p_j |v_i-v_j| / mean(v).
  // There are only six groups, regardless of the population size.
  let gini = 0;
  if (mean > 0) {
    for (let i = 0; i < occupied.length; i += 1) {
      for (let j = i + 1; j < occupied.length; j += 1) {
        gini += (occupied[i].count / population) * (occupied[j].count / population)
          * (Math.abs(occupied[i].benefit - occupied[j].benefit) / mean);
      }
    }
  }
  gini = Math.min(1, Math.max(0, gini));

  const lorenz = [{ x: 0, y: 0 }];
  let x = 0;
  let y = 0;
  for (const group of sorted) {
    x += group.count / population;
    y += totalBenefit > 0 ? (group.count * group.benefit) / totalBenefit : group.count / population;
    lorenz.push({ x, y });
  }
  // Preserve the exact plotting endpoint despite accumulated roundoff.
  lorenz[lorenz.length - 1] = { x: 1, y: 1 };

  return {
    params, budget, capture, productionCost, groups, chainCount,
    maxBenefit, minBenefit, ratio, gini, lorenz, totalBenefit,
    maxExtra: Math.max(...occupied.map(group => group.extra)),
  };
}
