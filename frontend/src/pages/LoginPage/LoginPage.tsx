import { useState } from 'react';
import type { ChangeEvent, FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { AuthLayout } from '../../components/AuthLayout/AuthLayout';
import { Button } from '../../components/Button/Button';
import { InputField } from '../../components/InputField/InputField';
import { PasswordInput } from '../../components/PasswordInput/PasswordInput';
import { Divider } from '../../components/Divider/Divider';
import { useLogin } from '../../hooks/useLogin';
import styles from './LoginPage.module.css';

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

  const onSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    void login({ email });
  };

  const right = (
    <section className={styles.right}>
      <h1 className={styles.heading}>Sign in</h1>
      <div className={styles.sub}>Use your email and password.</div>

      <form onSubmit={onSubmit} noValidate>
        <InputField
          label="Email"
          name="email"
          type="email"
          value={email}
          onChange={onEmailChange}
          placeholder="you@domain.com"
          autoComplete="email"
          required
        />

        <PasswordInput
          label="Password"
          name="password"
          value={password}
          onChange={onPasswordChange}
          placeholder="••••••••"
          autoComplete="current-password"
          required
          labelAction={
            <button type="button" className={styles.forgotLink}>
              Forgot password?
            </button>
          }
        />

        {error ? <div className={styles.formError}>{error}</div> : null}
        {success && !error ? <div className={styles.formSuccess}>Signed in</div> : null}

        <Button variant="accent" type="submit" disabled={loading}>
          Sign in
        </Button>
      </form>

      <Divider label="NEW HERE" />

      <Button as={Link} to="/register" variant="secondary">
        Create an account
      </Button>
    </section>
  );

  return <AuthLayout right={right} />;
}
