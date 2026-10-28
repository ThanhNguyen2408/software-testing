import {
  checkFormEmpty,
  checkMobile,
  checkPinCode,
  checkEmail,
  checkPassword,
} from './CheckProperty';

test('form thiếu trường bị từ chối', () => {
  expect(checkFormEmpty({}).status).toBe(false);
});

test('SĐT sai độ dài bị từ chối', () => {
  expect(checkMobile('123').status).toBe(false);
  expect(checkMobile('0912345678').status).toBe(true);
});

test('Pin code sai độ dài bị từ chối', () => {
  expect(checkPinCode('123').status).toBe(false);
  expect(checkPinCode('123456').status).toBe(true);
});

test('email sai định dạng bị từ chối', () => {
  expect(checkEmail('abc').status).toBe(false);
  expect(checkEmail('a@b.com').status).toBe(true);
});

test('mật khẩu quá ngắn bị từ chối', () => {
  expect(checkPassword('Ab#1').status).toBe(false);
});

test('mật khẩu hợp lệ được chấp nhận', () => {
  expect(checkPassword('Abc#1234').status).toBe(true);
});

// Các test dưới đây ghi nhận lỗi nghi vấn: khi lỗi được sửa, đổi kết quả mong đợi
test('BUG-14: SĐT chứa chữ cái vẫn được chấp nhận', () => {
  expect(checkMobile('09123abcde').status).toBe(true);
});

test('BUG-01: mật khẩu thiếu chữ hoa vẫn được chấp nhận', () => {
  expect(checkPassword('abc#1234').status).toBe(true);
});
