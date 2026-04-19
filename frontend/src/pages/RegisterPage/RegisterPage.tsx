import { useState } from 'react';
import type { ChangeEvent, FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { AuthLayout } from '../../components/AuthLayout/AuthLayout';
import { Button } from '../../components/Button/Button';
import { InputField } from '../../components/InputField/InputField';
import { PasswordInput } from '../../components/PasswordInput/PasswordInput';
import { useRegister } from '../../hooks/useRegister';
import styles from './RegisterPage.module.css';

export function RegisterPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { register, loading, error, success, reset } = useRegister();

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
      setName('');
      setEmail('');
      setPassword('');
    }
  };

  const right = (
    <section className={styles.right}>
      <h1 className={styles.heading}>Create account</h1>
      <div className={styles.sub}>One email, one password — that&apos;s all we need.</div>

      <form onSubmit={onSubmit} noValidate>
        <InputField
          label="Name (optional)"
          name="name"
          type="text"
          value={name}
          onChange={onNameChange}
          placeholder="Your name (optional)"
          autoComplete="name"
        />

        <InputField
          label="Email"
          name="email"
          type="email"
          value={email}
          onChange={onEmailChange}
          placeholder="you@example.com"
          autoComplete="email"
          required
        />

        <PasswordInput
          label="Password"
          name="password"
          value={password}
          onChange={onPasswordChange}
          placeholder="At least 5 characters"
          autoComplete="new-password"
          required
        />

        {error ? <div className={styles.formError}>{error}</div> : null}
        {success && !error ? <div className={styles.formSuccess}>Account created</div> : null}

        <Button variant="accent" type="submit" disabled={loading}>
          Create account
        </Button>
      </form>

      <div className={styles.footerLine}>
        Already have an account?{' '}
        <Link to="/login" className={styles.footerLink}>
          Sign in
        </Link>
      </div>
    </section>
  );

  return <AuthLayout right={right} />;
}
