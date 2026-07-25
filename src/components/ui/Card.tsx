import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

export type CardProps = HTMLAttributes<HTMLDivElement> & {
  children: ReactNode;
};

// Simple content container used by pages and future dashboard widgets.
export function Card({ children, className, ...props }: CardProps) {
  return (
    <section
      className={cn("rounded-xl border border-slate-200 bg-white p-6 shadow-sm", className)}
      {...props}
    >
      {children}
    </section>
  );
}
