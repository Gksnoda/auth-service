import { useCallback, useState } from 'react';
import { register as registerRequest } from '../lib/auth';
import { ApiError, NetworkError } from '../lib/apiClient';
import type { RegisterPayload } from '../types/auth';

export interface UseRegisterResult {
  register: (payload: RegisterPayload) => Promise<boolean>;
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

export function useRegister(): UseRegisterResult {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const register = useCallback(async (payload: RegisterPayload): Promise<boolean> => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      await registerRequest(payload);
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

  return { register, loading, error, success, reset };
}
