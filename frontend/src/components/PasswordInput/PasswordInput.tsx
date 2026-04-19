import type { ChangeEvent, KeyboardEvent, ReactNode } from 'react';
import { InputField } from '../InputField/InputField';
import { usePasswordVisibility } from '../../hooks/usePasswordVisibility';
import styles from './PasswordInput.module.css';

export interface PasswordInputProps {
  label: string;
  htmlFor?: string;
  name: string;
  value: string;
  onChange: (event: ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  autoComplete?: string;
  required?: boolean;
  error?: string | null;
  labelAction?: ReactNode;
}

export function PasswordInput({
  label,
  htmlFor,
  name,
  value,
  onChange,
  placeholder,
  autoComplete,
  required,
  error,
  labelAction,
}: PasswordInputProps) {
  const { visible, toggle, inputType } = usePasswordVisibility();

  const onKeyDown = (event: KeyboardEvent<HTMLSpanElement>) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      toggle();
    }
  };

  const eye = (
    <span
      className={styles.eye}
      role="button"
      tabIndex={0}
      aria-label={visible ? 'Hide password' : 'Show password'}
      onClick={toggle}
      onKeyDown={onKeyDown}
    >
      {visible ? 'hide' : 'show'}
    </span>
  );

  return (
    <InputField
      label={label}
      htmlFor={htmlFor}
      name={name}
      type={inputType}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      autoComplete={autoComplete}
      required={required}
      error={error}
      labelAction={labelAction}
      rightSlot={eye}
    />
  );
}
