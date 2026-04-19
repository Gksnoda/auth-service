import { useState } from 'react';
import type { ChangeEvent, FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { AuthLayout } from '@/components/AuthLayout/AuthLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { PasswordInput } from '@/components/ui/password-input';
import { useLogin } from '@/hooks/useLogin';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, loading, error, success, reset } = useLogin();

  const onEmailChange = (e: ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
    reset();
  };

  const onPasswordChange = (e: ChangeEvent<HTMLInputElement>) => {
    setPassword(e.target.value);
    reset();
  };

  const onSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    await login({ email, password });
  };

  const right = (
    <section className="flex flex-col justify-center px-11 py-14 max-sm:px-7 max-sm:py-8">
      <h1 className="font-heading text-[32px] font-bold leading-none mb-1">Sign in</h1>
      <p className="text-sm text-muted-foreground mb-6">Use your email and password.</p>

      <form onSubmit={onSubmit} noValidate className="flex flex-col gap-4">
        <div className="grid gap-1.5">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            name="email"
            type="email"
            value={email}
            onChange={onEmailChange}
            placeholder="you@domain.com"
            autoComplete="email"
            required
          />
        </div>

        <div className="grid gap-1.5">
          <div className="flex items-center justify-between">
            <Label htmlFor="password">Password</Label>
            <button
              type="button"
              className="text-sm text-muted-foreground underline decoration-wavy underline-offset-2 hover:text-primary"
            >
              Forgot password?
            </button>
          </div>
          <PasswordInput
            id="password"
            name="password"
            value={password}
            onChange={onPasswordChange}
            placeholder="••••••••"
            autoComplete="current-password"
            required
          />
        </div>

        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        {success && !error ? <p className="text-sm text-primary">Signed in</p> : null}

        <Button type="submit" disabled={loading}>
          Sign in
        </Button>
      </form>

      <div className="my-6 flex items-center gap-3">
        <Separator className="flex-1" />
        <span className="text-xs tracking-wider text-muted-foreground">NEW HERE</span>
        <Separator className="flex-1" />
      </div>

      <Button asChild variant="secondary">
        <Link to="/register">Create an account</Link>
      </Button>
    </section>
  );

  return <AuthLayout right={right} />;
}
