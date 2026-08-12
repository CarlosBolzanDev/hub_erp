"use client";

import { useActionState } from "react";
import { useFormStatus } from "react-dom";
import { loginAction, type LoginState } from "@/services/auth/actions";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

const initialState: LoginState = { message: null };

function SubmitButton() {
  const { pending } = useFormStatus();
  return <Button type="submit" className="w-full" isLoading={pending}>Entrar</Button>;
}

export function LoginForm() {
  const [state, formAction] = useActionState(loginAction, initialState);

  return (
    <form action={formAction} className="space-y-5" noValidate>
      <Input label="E-mail" name="email" type="email" placeholder="voce@empresa.com" autoComplete="email" required />
      <Input label="Senha" name="password" type="password" placeholder="Sua senha" autoComplete="current-password" required minLength={6} />
      {state.message ? <div className="rounded-[var(--radius-md)] border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200" role="alert">{state.message}</div> : null}
      <SubmitButton />
    </form>
  );
}
