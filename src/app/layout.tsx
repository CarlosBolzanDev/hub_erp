import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Bibly",
  description: "SaaS para gerenciamento e conferência de pedidos de marketplaces.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="pt-BR"><body>{children}</body></html>;
}
