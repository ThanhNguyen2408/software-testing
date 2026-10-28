const INR_TO_VND_RATE = 300;

const parseAmount = (value) => {
  const amount = Number(String(value).replace(/,/g, ""));
  return Number.isFinite(amount) ? amount : 0;
};

export const inrToVnd = (value) =>
  Math.round((parseAmount(value) * INR_TO_VND_RATE) / 1000) * 1000;

export const vndToInr = (value) =>
  Math.round(parseAmount(value) / INR_TO_VND_RATE);

export const formatInrAsVnd = (value) =>
  new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
    maximumFractionDigits: 0,
  }).format(inrToVnd(value));