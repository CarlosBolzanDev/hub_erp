import type { ButtonHTMLAttributes, ReactNode } from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/utils/cn";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  isLoading?: boolean;
  variant?: "primary" | "secondary" | "ghost";
  children: ReactNode;
};

export function Button({ className, isLoading, disabled, variant = "primary", children, ...props }: ButtonProps) {
  const variants = {
    primary: "bg-[var(--color-primary)] text-white shadow-[var(--shadow-button)] hover:bg-[var(--color-primary-hover)]",
    secondary: "bg-[var(--color-surface-strong)] text-[var(--color-text)] border border-[var(--color-border)] hover:bg-[var(--color-surface-muted)]",
    ghost: "bg-transparent text-[var(--color-text-muted)] hover:bg-[var(--color-surface-muted)] hover:text-[var(--color-text)]",
  };

  return (
    <button
      className={cn(
        "inline-flex min-h-11 items-center justify-center gap-2 rounded-[var(--radius-md)] px-4 py-2 text-sm font-semibold transition-all duration-200",
        "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-focus)]",
        "active:translate-y-px disabled:cursor-not-allowed disabled:opacity-60",
        variants[variant],
        className,
      )}
      disabled={disabled || isLoading}
      aria-busy={isLoading || undefined}
      {...props}
    >
      {isLoading ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : null}
      {children}
    </button>
  );
}
