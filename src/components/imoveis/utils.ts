import type { Fatura } from '@/types/imoveis';
export const money = (v?: number | null) => (v ?? 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
export const date = (v?: string | null) => v ? new Date(v).toLocaleDateString('pt-BR') : '-';
export const isOverdue = (f: Fatura) => f.status === 'vencida' || (!f.data_pagamento && !!f.data_vencimento && new Date(f.data_vencimento) < new Date());
export const invoiceClass = (f: Fatura) => f.status === 'paga' ? 'paid' : isOverdue(f) ? 'overdue' : 'pending';
