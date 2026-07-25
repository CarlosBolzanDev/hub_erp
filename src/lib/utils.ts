import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

// Combines conditional class names and resolves TailwindCSS conflicts for reusable components.
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
