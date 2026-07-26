import type { Imovel } from '@/types/imoveis';
import { invoiceClass, isOverdue, money } from './utils';
export function ImovelCard({ imovel, onClick }: { imovel: Imovel; onClick: () => void }) {
  const pendentes = imovel.faturas?.filter((f) => f.status === 'pendente').length ?? 0;
  const vencidas = imovel.faturas?.filter(isOverdue).length ?? 0;
  const pagas = imovel.faturas?.filter((f) => f.status === 'paga').length ?? 0;
  return <article className="card" onClick={onClick}><div className="toolbar"><strong>{imovel.codigo}</strong><span className="badge">{imovel.situacao ?? 'Sem situação'}</span></div><h3>{imovel.nome}</h3><p className="muted">{imovel.tipo ?? '-'} • {imovel.cidade ?? '-'}/{imovel.estado ?? '-'}</p><p><b>Aluguel:</b> {money(imovel.valor_aluguel)}</p><p><b>Proprietário:</b> {imovel.proprietarios?.nome ?? 'Não informado'}</p><div><span className="badge paid">{pagas} pagas</span> <span className="badge pending">{pendentes} pendentes</span> <span className="badge overdue">{vencidas} vencidas</span></div></article>;
}
