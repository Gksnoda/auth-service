import { useCallback, useState } from 'react';
import { login as loginRequest } from '../lib/auth';
import { ApiError, NetworkError } from '../lib/apiClient';
import type { LoginCredentials } from '../types/auth';

export interface UseLoginResult {
  login: (credentials: LoginCredentials) => Promise<boolean>;
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

  const login = useCallback(async (credentials: LoginCredentials): Promise<boolean> => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      await loginRequest(credentials);
      setSuccess(true);
      return true;
    } catch (err) {
      setError(toMessage(err));
      return false;
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
