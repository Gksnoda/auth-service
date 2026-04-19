import { useState } from 'react';
import type { ChangeEvent, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthLayout } from '@/components/AuthLayout/AuthLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { PasswordInput } from '@/components/ui/password-input';
import { useRegister } from '@/hooks/useRegister';

export function RegisterPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { register, loading, error, success, reset } = useRegister();
  const navigate = useNavigate();

  const onNameChange = (e: ChangeEvent<HTMLInputElement>) => {
    setName(e.target.value);
    reset();
  };

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
    const ok = await register({ name: name || null, email, password });
    if (ok) {
      navigate('/login');
    }
  };

  const right = (
    <section className="flex flex-col justify-center px-11 py-14 max-sm:px-7 max-sm:py-8">
      <h1 className="font-heading text-[32px] font-bold leading-none mb-1">Create account</h1>
      <p className="text-sm text-muted-foreground mb-6">
        One email, one password — that&apos;s all we need.
      </p>

      <form onSubmit={onSubmit} noValidate className="flex flex-col gap-4">
        <div className="grid gap-1.5">
          <Label htmlFor="name">Name (optional)</Label>
          <Input
            id="name"
            name="name"
            type="text"
            value={name}
            onChange={onNameChange}
            placeholder="Your name (optional)"
            autoComplete="name"
          />
        </div>

        <div className="grid gap-1.5">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            name="email"
            type="email"
            value={email}
            onChange={onEmailChange}
            placeholder="you@example.com"
            autoComplete="email"
            required
          />
        </div>

        <div className="grid gap-1.5">
          <Label htmlFor="password">Password</Label>
          <PasswordInput
            id="password"
            name="password"
            value={password}
            onChange={onPasswordChange}
            placeholder="At least 5 characters"
            autoComplete="new-password"
            required
          />
        </div>

        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        {success && !error ? <p className="text-sm text-primary">Account created</p> : null}

        <Button type="submit" disabled={loading}>
          Create account
        </Button>
      </form>

      <p className="mt-6 text-sm text-muted-foreground">
        Already have an account?{' '}
        <Link to="/login" className="text-primary underline underline-offset-2">
          Sign in
        </Link>
      </p>
    </section>
  );

  return <AuthLayout right={right} />;
}
