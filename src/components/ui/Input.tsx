import type { InputHTMLAttributes } from "react";
import { cn } from "@/utils/cn";

type InputProps = InputHTMLAttributes<HTMLInputElement> & { label: string; error?: string };

export function Input({ id, label, error, className, ...props }: InputProps) {
  const inputId = id ?? props.name;
  return (
    <div className="space-y-2">
      <label htmlFor={inputId} className="block text-sm font-medium text-[var(--color-text)]">{label}</label>
      <input
        id={inputId}
        className={cn(
          "w-full rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-3 text-[var(--color-text)] shadow-inner outline-none transition",
          "placeholder:text-[var(--color-text-subtle)] focus:border-[var(--color-primary)] focus:ring-4 focus:ring-[var(--color-primary-soft)]",
          className,
        )}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? `${inputId}-error` : undefined}
        {...props}
      />
      {error ? <p id={`${inputId}-error`} className="text-sm text-[var(--color-danger)]">{error}</p> : null}
    </div>
  );
}
