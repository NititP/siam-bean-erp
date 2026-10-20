const twoDecimals = new Intl.NumberFormat("en-US", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

/** 9630 -> "9,630.00 THB". The one way money is shown in the app. */
export function formatTHB(amount: number | string): string {
  return `${twoDecimals.format(Number(amount))} THB`;
}
