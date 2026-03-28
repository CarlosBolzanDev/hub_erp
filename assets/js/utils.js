export const fmtMoney = (v) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v || 0);
export const uid = () => Math.random().toString(36).slice(2, 10);
