import { assertSupabaseEnv, supabase } from './supabase';
import type { Imovel, ImovelFilters, ImovelFormData, Proprietario } from '@/types/imoveis';

const imovelSelect = '*, proprietarios(*), faturas(*)';

export async function listarProprietarios() {
  assertSupabaseEnv();
  const { data, error } = await supabase.from('proprietarios').select('*').order('nome');
  if (error) throw error;
  return (data ?? []) as Proprietario[];
}

export async function listarImoveis(filters: ImovelFilters) {
  assertSupabaseEnv();
  let query = supabase.from('imoveis').select(imovelSelect).order('created_at', { ascending: false });
  if (filters.codigo) query = query.ilike('codigo', `%${filters.codigo}%`);
  if (filters.nome) query = query.ilike('nome', `%${filters.nome}%`);
  if (filters.cidade) query = query.ilike('cidade', `%${filters.cidade}%`);
  if (filters.estado) query = query.ilike('estado', `%${filters.estado}%`);
  if (filters.tipo) query = query.eq('tipo', filters.tipo);
  if (filters.situacao) query = query.eq('situacao', filters.situacao);
  if (filters.aluguelMin) query = query.gte('valor_aluguel', Number(filters.aluguelMin));
  if (filters.aluguelMax) query = query.lte('valor_aluguel', Number(filters.aluguelMax));
  if (filters.vendaMin) query = query.gte('valor_venda', Number(filters.vendaMin));
  if (filters.vendaMax) query = query.lte('valor_venda', Number(filters.vendaMax));
  const { data, error } = await query;
  if (error) throw error;
  let imoveis = (data ?? []) as Imovel[];
  if (filters.proprietario) imoveis = imoveis.filter((i) => i.proprietarios?.nome?.toLowerCase().includes(filters.proprietario.toLowerCase()));
  if (filters.faturasPendentes) imoveis = imoveis.filter((i) => i.faturas?.some((f) => f.status === 'pendente'));
  if (filters.faturasVencidas) imoveis = imoveis.filter((i) => i.faturas?.some((f) => f.status === 'vencida' || (!f.data_pagamento && f.data_vencimento && new Date(f.data_vencimento) < new Date())));
  return imoveis;
}

export async function criarImovel(payload: ImovelFormData) {
  assertSupabaseEnv();
  if (!payload.proprietario_id) throw new Error('Selecione um proprietário para cadastrar o imóvel.');
  const { data, error } = await supabase.from('imoveis').insert(payload).select(imovelSelect).single();
  if (error) throw error;
  return data as Imovel;
}

export async function editarImovel(id: string, payload: ImovelFormData) {
  assertSupabaseEnv();
  if (!payload.proprietario_id) throw new Error('Selecione um proprietário para manter o vínculo do imóvel.');
  const { data, error } = await supabase.from('imoveis').update(payload).eq('id', id).select(imovelSelect).single();
  if (error) throw error;
  return data as Imovel;
}
