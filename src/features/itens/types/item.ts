// Domain entity used by the future Itens CRUD implementation.
export type Item = {
  id: string;
  name: string;
  description?: string | null;
  createdAt: string;
  updatedAt: string;
};

export type CreateItemInput = {
  name: string;
  description?: string | null;
};

export type UpdateItemInput = Partial<CreateItemInput>;
