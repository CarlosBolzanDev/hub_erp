export type UserRole = "ADMIN" | "PERSONAL";
export type PropertyStatus = "ATIVO" | "INATIVO" | "VENDIDO";
export type InstallmentStatus = "PENDENTE" | "PAGO" | "ATRASADO";
export type Property = { id: string; name: string; type: string | null; status: PropertyStatus; price: number | null; sold_price: number | null; installments_count: number | null; owner_name: string | null; owner_document: string | null; owner_phone: string | null; owner_email: string | null; notes: string | null; zip_code: string | null; street: string | null; number: string | null; complement: string | null; neighborhood: string | null; city: string | null; state: string | null; created_at?: string; updated_at?: string; };
export type PropertyInstallment = { id: string; property_id: string; installment_number: number; amount: number; due_date: string; payment_date: string | null; status: InstallmentStatus; comprovante_url: string | null; notes: string | null; };
export type PropertyContract = { id: string; property_id: string; file_url: string; file_type: string | null; created_at: string; };
export type PropertyDetails = Property & { installments: PropertyInstallment[]; contract: PropertyContract | null };
export type PropertyFilters = { search?: string; status?: string; type?: string; page?: number };
