import { createClient } from "@/lib/supabase/server";
import type { CreateItemInput, Item, UpdateItemInput } from "@/features/itens/types/item";

// Service boundary for the Itens domain. Methods are intentionally prepared for future CRUD wiring.
export const itemsService = {
  async list(): Promise<Item[]> {
    await createClient();
    return [];
  },

  async create(_input: CreateItemInput): Promise<Item | null> {
    await createClient();
    return null;
  },

  async update(_id: string, _input: UpdateItemInput): Promise<Item | null> {
    await createClient();
    return null;
  },

  async remove(_id: string): Promise<void> {
    await createClient();
  },
};
