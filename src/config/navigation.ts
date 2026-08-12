import { LayoutDashboard, PackageCheck, Users } from "lucide-react";

export const navigationItems = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Pedidos", href: "/pedidos", icon: PackageCheck },
  { label: "Usuários", href: "/usuarios", icon: Users },
] as const;
