import type { ComponentPropsWithoutRef, ElementType, ReactNode } from 'react';
import styles from './Button.module.css';

type ButtonVariant = 'accent' | 'secondary' | 'default';

type BaseProps = {
  variant?: ButtonVariant;
  disabled?: boolean;
  children: ReactNode;
};

export type ButtonProps<T extends ElementType = 'button'> = BaseProps & {
  as?: T;
} & Omit<ComponentPropsWithoutRef<T>, keyof BaseProps | 'as'>;

export function Button<T extends ElementType = 'button'>({
  as,
  variant = 'default',
  disabled,
  children,
  ...rest
}: ButtonProps<T>) {
  const Component = (as ?? 'button') as ElementType;
  const className = [
    styles.btn,
    variant === 'accent' ? styles.accent : '',
    variant === 'secondary' ? styles.secondary : '',
  ]
    .filter(Boolean)
    .join(' ');

  const extraProps = as ? { 'aria-disabled': disabled || undefined } : { disabled };

  return (
    <Component className={className} {...extraProps} {...rest}>
      {children}
    </Component>
  );
}
