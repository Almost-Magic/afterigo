import { useEffect, useState } from 'react';
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline';
import { useTheme } from '../lib/theme';
import { api } from '../lib/api';

export default function Header() {
  const { theme, toggle } = useTheme();
  const [healthy, setHealthy] = useState(null);

  useEffect(() => {
    const check = () =>
      api.health()
        .then(() => setHealthy(true))
        .catch(() => setHealthy(false));
    check();
    const id = setInterval(check, 30000);
    return () => clearInterval(id);
  }, []);

  return (
    <header className="h-14 bg-surface dark:bg-surface border-b border-border flex items-center justify-between px-6 shrink-0">
      <div className="flex items-center gap-3">
        <h2 className="font-heading text-sm font-medium text-text-primary">Ripple CRM v3</h2>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-xs text-text-secondary">
          <span
            className={`w-2 h-2 rounded-full ${
              healthy === true ? 'bg-healthy' : healthy === false ? 'bg-critical' : 'bg-text-muted'
            }`}
          />
          {healthy === true ? 'Connected' : healthy === false ? 'Disconnected' : 'Checking...'}
        </div>
        <button
          onClick={toggle}
          className="p-1.5 rounded-lg hover:bg-surface-light text-text-secondary hover:text-text-primary transition-colors"
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
          {theme === 'dark' ? <SunIcon className="w-5 h-5" /> : <MoonIcon className="w-5 h-5" />}
        </button>
      </div>
    </header>
  );
}
