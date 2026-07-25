import "./globals.css";
import { Toaster } from "sonner";
export default function RootLayout({ children }: { children: React.ReactNode }) { return <html lang="pt-BR"><body><Toaster richColors />{children}</body></html>; }
