import { useCallback, useState } from 'react';

export interface UsePasswordVisibilityResult {
  visible: boolean;
  toggle: () => void;
  inputType: 'text' | 'password';
}

export function usePasswordVisibility(): UsePasswordVisibilityResult {
  const [visible, setVisible] = useState(false);
  const toggle = useCallback(() => setVisible((v) => !v), []);
  const inputType: 'text' | 'password' = visible ? 'text' : 'password';
  return { visible, toggle, inputType };
}
