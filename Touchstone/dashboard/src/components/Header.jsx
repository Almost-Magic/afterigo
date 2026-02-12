import { useTheme } from '../lib/theme';
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline';

export default function Header() {
  const { theme, toggle } = useTheme();

  return (
    <header className="h-12 border-b border-border bg-surface dark:bg-surface flex items-center justify-between px-4 shrink-0">
      <div className="text-xs text-text-muted">
        Open Source Marketing Attribution
      </div>
      <button
        onClick={toggle}
        className="p-1.5 rounded-lg text-text-secondary hover:text-text-primary hover:bg-surface-light transition-colors"
        title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
      >
        {theme === 'dark' ? <SunIcon className="w-4 h-4" /> : <MoonIcon className="w-4 h-4" />}
      </button>
    </header>
  );
}
