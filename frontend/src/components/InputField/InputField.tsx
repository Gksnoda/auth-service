import type { ChangeEvent, ReactNode } from 'react';
import styles from './InputField.module.css';

export interface InputFieldProps {
  label: string;
  htmlFor?: string;
  name: string;
  type?: string;
  value: string;
  onChange: (event: ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  autoComplete?: string;
  required?: boolean;
  error?: string | null;
  labelAction?: ReactNode;
  rightSlot?: ReactNode;
}

export function InputField({
  label,
  htmlFor,
  name,
  type = 'text',
  value,
  onChange,
  placeholder,
  autoComplete,
  required,
  error,
  labelAction,
  rightSlot,
}: InputFieldProps) {
  const id = htmlFor ?? name;
  const wrapClassName = [styles.inputWrap, error ? styles.inputWrapError : '']
    .filter(Boolean)
    .join(' ');

  return (
    <div className={styles.field}>
      <label className={styles.label} htmlFor={id}>
        <span>{label}</span>
        {labelAction ? <span>{labelAction}</span> : null}
      </label>
      <div className={wrapClassName}>
        <input
          id={id}
          name={name}
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          autoComplete={autoComplete}
          required={required}
        />
        {rightSlot}
      </div>
      {error ? <div className={styles.err}>{error}</div> : null}
    </div>
  );
}
