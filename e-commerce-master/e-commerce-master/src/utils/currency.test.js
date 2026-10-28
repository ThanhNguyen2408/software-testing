import { inrToVnd, vndToInr, formatInrAsVnd } from './currency';

test('inrToVnd quy đổi và làm tròn đến nghìn', () => {
  expect(inrToVnd(1000)).toBe(300000);
  expect(inrToVnd('1,000')).toBe(300000);
});

test('giá trị không hợp lệ trả về 0', () => {
  expect(inrToVnd('abc')).toBe(0);
});

test('vndToInr quy đổi ngược', () => {
  expect(vndToInr(300000)).toBe(1000);
});

test('formatInrAsVnd có ký hiệu ₫', () => {
  expect(formatInrAsVnd(1000)).toContain('₫');
});
