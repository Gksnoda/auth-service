import styles from './BrandPanel.module.css';

export function BrandPanel() {
  return (
    <aside className={styles.left}>
      <div className={styles.tagline}>
        Hi, I&apos;m <em>Gustavo</em>.
      </div>
      <div className={styles.desc}>
        This is me practicing — a small personal auth project I&apos;m building to get my hands
        dirty with login flows. Nothing fancy, just me learning in public.
      </div>

      <div className={styles.socialLinks}>
        <a
          className={styles.socialChip}
          href="https://linkedin.com/in/gustavo-dev"
          target="_blank"
          rel="noopener"
        >
          <span className={styles.sIco}>in</span>
          <span>LinkedIn</span>
          <span className={styles.sArrow}>↗</span>
        </a>
        <a
          className={styles.socialChip}
          href="https://github.com/gustavo-dev"
          target="_blank"
          rel="noopener"
        >
          <span className={styles.sIco}>◐</span>
          <span>GitHub</span>
          <span className={styles.sArrow}>↗</span>
        </a>
      </div>

      <div className={styles.leftFooter}>
        <span className={styles.ribbon}>personal project</span>
        <span className={styles.ribbon}>learning</span>
      </div>
    </aside>
  );
}
