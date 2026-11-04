import assert from 'node:assert/strict';
import test from 'node:test';
import { computeModel, DEFAULTS } from '../site/model.mjs';

function close(actual, expected, tolerance = 1e-12) {
  assert.ok(Math.abs(actual - expected) <= tolerance * Math.max(1, Math.abs(expected)),
    `${actual} differs from ${expected}`);
}

test('the default example partitions public spending once and preserves the population', () => {
  const model = computeModel();
  assert.equal(model.budget, 200_000_000_000);
  assert.equal(model.capture, 20_000_000_000);
  assert.equal(model.productionCost, 180_000_000_000);
  assert.equal(model.chainCount, 11_111);
  assert.equal(model.groups.reduce((sum, group) => sum + group.count, 0), DEFAULTS.population);
  assert.equal(model.groups.reduce((sum, group) => sum + group.pool, 0), model.capture);
  assert.equal(model.budget, model.capture + model.productionCost);
  assert.equal(model.totalBenefit, model.budget + model.capture);
  assert.equal(model.groups.at(-1).extra, 4_000_000_000);
  assert.equal(model.groups[1].extra, 400_000);
  assert.equal(model.ratio, 2_000_001);
});

test('equal level pools imply inverse counts on a geometric additional-income grid', () => {
  for (const branching of [2, 3, 10, 20]) {
    const { groups, capture } = computeModel({ branching, owners: 3 });
    for (const group of groups.slice(1)) close(group.count * group.extra, capture / 5);
    for (let j = 2; j < groups.length; j += 1) close(groups[j].extra / groups[j - 1].extra, branching);
  }
});

test('a universal dividend produces equal benefits with and without uniform funding', () => {
  for (const tax of [false, true]) {
    const model = computeModel({ allocation: 'people', tax });
    for (const group of model.groups) close(group.extra, 200);
    close(model.minBenefit, tax ? 200 : 2200);
    close(model.maxBenefit, model.minBenefit);
    close(model.ratio, 1);
    close(model.gini, 0);
    for (const point of model.lorenz) close(point.x, point.y);
  }
});

test('uniform funding subtracts one price per citizen without changing captured money', () => {
  const gross = computeModel();
  const funded = computeModel({ tax: true });
  close(gross.totalBenefit - funded.totalBenefit, gross.budget);
  close(funded.totalBenefit, funded.capture);
  for (let j = 0; j < gross.groups.length; j += 1) {
    close(gross.groups[j].benefit - funded.groups[j].benefit, DEFAULTS.price);
    assert.equal(gross.groups[j].pool, funded.groups[j].pool);
  }
  assert.equal(funded.ratio, Infinity);
  close(gross.gini * gross.totalBenefit, funded.gini * funded.totalBenefit);
});

test('zero capture and zero total benefits have explicit equality conventions', () => {
  for (const tax of [false, true]) {
    const model = computeModel({ margin: 0, tax });
    assert.equal(model.gini, 0);
    assert.equal(model.ratio, 1);
    assert.equal(model.maxExtra, 0);
    assert.equal(model.totalBenefit, tax ? 0 : model.budget);
    for (const point of model.lorenz) close(point.x, point.y);
  }
});

test('grouped Gini and Lorenz area match independently expanded citizens', () => {
  for (const allocation of ['levels', 'people', 'top']) {
    for (const tax of [false, true]) {
      const model = computeModel({ population: 40, branching: 2, owners: 1, price: 7, margin: 0.37, allocation, tax });
      const citizens = model.groups.flatMap(group => Array(group.count).fill(group.benefit));
      const pairDifference = citizens.reduce((sum, a) => sum + citizens.reduce((inner, b) => inner + Math.abs(a - b), 0), 0);
      const bruteGini = pairDifference / (2 * citizens.length * citizens.reduce((sum, value) => sum + value, 0));
      close(model.gini, bruteGini);
      let twiceArea = 0;
      for (let j = 1; j < model.lorenz.length; j += 1) {
        const a = model.lorenz[j - 1];
        const b = model.lorenz[j];
        assert.ok(b.x >= a.x && b.y >= a.y);
        twiceArea += (b.x - a.x) * (a.y + b.y);
      }
      close(model.gini, 1 - twiceArea);
      assert.deepEqual(model.lorenz.at(-1), { x: 1, y: 1 });
    }
  }
});

test('an empty general-citizen group does not alter extrema or lose money', () => {
  const model = computeModel({ population: 31, branching: 2, tax: true });
  assert.equal(model.groups[0].count, 0);
  assert.equal(model.groups[0].extra, 0);
  assert.ok(model.minBenefit > 0);
  assert.equal(model.ratio, 16);
  close(model.totalBenefit, model.capture);
});

test('top-weighted allocation uses five ninths at the factory and conserves the pool', () => {
  const model = computeModel({ allocation: 'top' });
  close(model.groups.at(-1).pool, model.capture * 5 / 9);
  close(model.groups.reduce((sum, group) => sum + group.pool, 0), model.capture);
  close(model.groups.at(-1).pool, model.groups[1].pool * 5);
});

test('changing currency scales all monetary outputs and leaves inequality unchanged', () => {
  const first = computeModel({ price: 1 });
  const second = computeModel({ price: 37 });
  close(second.totalBenefit, 37 * first.totalBenefit);
  close(second.maxExtra, 37 * first.maxExtra);
  close(second.gini, first.gini);
  close(second.ratio, first.ratio);
});

test('invalid populations, budgets, group sizes and rules are rejected', () => {
  const invalid = [
    { population: 0 }, { population: 1.5 }, { population: Infinity }, { population: '100000000' },
    { price: 0 }, { price: -1 }, { price: NaN }, { price: Infinity }, { price: Number.MAX_VALUE },
    { margin: -0.1 }, { margin: 1.1 }, { margin: NaN },
    { branching: 1 }, { branching: 21 }, { branching: 2.5 },
    { owners: 0 }, { owners: 0.5 }, { owners: Number.MAX_SAFE_INTEGER },
    { population: 30, branching: 2 }, { allocation: 'unknown' }, { tax: 'yes' },
  ];
  for (const params of invalid) assert.throws(() => computeModel(params), RangeError, JSON.stringify(params));
});
