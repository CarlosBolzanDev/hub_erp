export const onlyDigits = (value?: string | null) => (value ?? "").replace(/\D/g, "");
export const formatCurrency = (value?: number | string | null) => value == null || value === "" ? "—" : new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(Number(value));
export const formatDate = (value?: string | null) => value ? new Intl.DateTimeFormat("pt-BR", { timeZone: "UTC" }).format(new Date(`${value}T00:00:00Z`)) : "—";
export function formatCpfCnpj(value?: string | null) { const d = onlyDigits(value); if (d.length <= 11) return d.replace(/(\d{3})(\d{3})(\d{3})(\d{0,2})/, "$1.$2.$3-$4").replace(/[-.]$/g, ""); return d.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{0,2})/, "$1.$2.$3/$4-$5").replace(/[-/.]$/g, ""); }
export const formatCep = (value?: string | null) => onlyDigits(value).replace(/(\d{5})(\d{0,3})/, "$1-$2").replace(/-$/g, "");
export const formatPhone = (value?: string | null) => { const d = onlyDigits(value); return d.length > 10 ? d.replace(/(\d{2})(\d{5})(\d{0,4})/, "($1) $2-$3").replace(/-$/g, "") : d.replace(/(\d{2})(\d{4})(\d{0,4})/, "($1) $2-$3").replace(/-$/g, ""); };
