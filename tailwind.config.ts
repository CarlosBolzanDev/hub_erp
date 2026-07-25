import type { Config } from "tailwindcss";
const config: Config = { darkMode: "class", content: ["./src/**/*.{ts,tsx}"], theme: { extend: { keyframes: { "fade-up": { from: { opacity: "0", transform: "translateY(10px)" }, to: { opacity: "1", transform: "translateY(0)" } } }, animation: { "fade-up": "fade-up .25s ease-out both" } } }, plugins: [] };
export default config;
