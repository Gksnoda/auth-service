import styles from './Divider.module.css';

export interface DividerProps {
  label: string;
}

export function Divider({ label }: DividerProps) {
  return <div className={styles.orDiv}>{label}</div>;
}
