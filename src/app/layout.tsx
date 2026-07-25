import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";
import "./globals.css";

export const metadata: Metadata = {
  title: "Hub ERP",
  description: "Estrutura inicial do Hub ERP com Next.js, Supabase e TailwindCSS.",
};

// Root layout using App Router and a persistent shell for future authenticated areas.
export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body>
        <Sidebar />
        <div className="min-h-screen pl-64">
          <Header />
          <main className="px-8 py-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
