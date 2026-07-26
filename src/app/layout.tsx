import type { ReactNode } from 'react';
import './globals.css';
import Link from 'next/link';

export default function RootLayout({ children }: { children: ReactNode }) {
  return <html lang="pt-BR"><body><aside><h1>Hub ERP</h1><Link href="/">Início</Link><Link href="/imoveis">Imóveis</Link></aside><main>{children}</main></body></html>;
}
