import type { ReactNode } from 'react';
import { BrandPanel } from '../BrandPanel/BrandPanel';
import styles from './AuthLayout.module.css';

export interface AuthLayoutProps {
  left?: ReactNode;
  right: ReactNode;
}

export function AuthLayout({ left, right }: AuthLayoutProps) {
  return (
    <main className={styles.card}>
      <div className={styles.split}>
        {left ?? <BrandPanel />}
        {right}
      </div>
    </main>
  );
}
