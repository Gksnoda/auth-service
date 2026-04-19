import { useCallback, useState } from 'react';
import { login as loginRequest } from '../lib/auth';
import { ApiError, NetworkError } from '../lib/apiClient';
import type { LoginCredentials, LoginResponse } from '../types/auth';

export interface UseLoginResult {
  login: (credentials: LoginCredentials) => Promise<LoginResponse | null>;
  loading: boolean;
  error: string | null;
  success: boolean;
  reset: () => void;
}

function toMessage(err: unknown): string {
  if (err instanceof NetworkError) return err.message;
  if (err instanceof ApiError) return err.message;
  return 'Unexpected error. Please try again.';
}

export function useLogin(): UseLoginResult {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const login = useCallback(async (credentials: LoginCredentials): Promise<LoginResponse | null> => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      const data = await loginRequest(credentials);
      setSuccess(true);
      return data;
    } catch (err) {
      setError(toMessage(err));
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setError(null);
    setSuccess(false);
  }, []);

  return { login, loading, error, success, reset };
}
