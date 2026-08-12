export type PedidoStatus = "pendente" | "separando" | "conferido" | "expedido";

export type Pedido = {
  id: string;
  marketplace: string;
  external_id: string;
  status: PedidoStatus;
  created_at: string;
};
