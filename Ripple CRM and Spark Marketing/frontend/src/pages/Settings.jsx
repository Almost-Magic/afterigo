import { useEffect, useState } from 'react';
import { useTheme } from '../lib/theme';
import {
  Cog6ToothIcon,
  SunIcon,
  MoonIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

const CURRENCIES = ['AUD', 'USD', 'EUR', 'GBP', 'NZD', 'SGD', 'INR'];

export default function Settings() {
  const { theme, toggle } = useTheme();
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteResult, setDeleteResult] = useState(null);

  useEffect(() => {
    fetch('/api/settings')
      .then((r) => r.json())
      .then((d) => { setSettings(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const save = async () => {
    setSaving(true);
    setSaved(false);
    try {
      const res = await fetch('/api/settings', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      });
      if (res.ok) {
        setSettings(await res.json());
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
      }
    } finally {
      setSaving(false);
    }
  };

  const deleteAllData = async () => {
    try {
      const res = await fetch('/api/settings/data', { method: 'DELETE' });
      if (res.ok) {
        setDeleteResult(await res.json());
        setShowDeleteConfirm(false);
      }
    } catch {
      /* ignore */
    }
  };

  if (loading || !settings) {
    return <p className="text-text-muted text-center py-12">Loading settings...</p>;
  }

  const weights = settings.health_weights || {};

  return (
    <div className="space-y-8 max-w-2xl">
      <div className="flex items-center gap-3">
        <Cog6ToothIcon className="w-7 h-7 text-gold" />
        <h1 className="font-heading text-2xl font-semibold text-text-primary">Settings</h1>
      </div>

      {/* Profile */}
      <section className="bg-surface rounded-xl border border-border p-6 space-y-4">
        <h2 className="font-heading text-lg font-semibold text-text-primary">Profile</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-text-secondary mb-1">Name</label>
            <input
              value={settings.user_name || ''}
              onChange={(e) => setSettings({ ...settings, user_name: e.target.value })}
              className="w-full bg-surface-light border border-border rounded-lg px-3 py-2 text-sm text-text-primary"
            />
          </div>
          <div>
            <label className="block text-sm text-text-secondary mb-1">Email</label>
            <input
              value={settings.user_email || ''}
              onChange={(e) => setSettings({ ...settings, user_email: e.target.value })}
              className="w-full bg-surface-light border border-border rounded-lg px-3 py-2 text-sm text-text-primary"
            />
          </div>
        </div>
      </section>

      {/* Appearance */}
      <section className="bg-surface rounded-xl border border-border p-6 space-y-4">
        <h2 className="font-heading text-lg font-semibold text-text-primary">Appearance</h2>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-text-primary">Theme</p>
            <p className="text-xs text-text-muted">Current: {theme === 'dark' ? 'Dark' : 'Light'}</p>
          </div>
          <button
            onClick={toggle}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-surface-light border border-border text-sm text-text-primary hover:bg-gold/10 transition-colors"
          >
            {theme === 'dark' ? <SunIcon className="w-4 h-4" /> : <MoonIcon className="w-4 h-4" />}
            Switch to {theme === 'dark' ? 'Light' : 'Dark'}
          </button>
        </div>
        <div>
          <label className="block text-sm text-text-secondary mb-1">Default Currency</label>
          <select
            value={settings.currency || 'AUD'}
            onChange={(e) => setSettings({ ...settings, currency: e.target.value })}
            className="bg-surface-light border border-border rounded-lg px-3 py-2 text-sm text-text-primary"
          >
            {CURRENCIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      </section>

      {/* Health Score Weights */}
      <section className="bg-surface rounded-xl border border-border p-6 space-y-4">
        <h2 className="font-heading text-lg font-semibold text-text-primary">Relationship Score Weights</h2>
        <p className="text-xs text-text-muted">Adjust how each factor contributes to the health score. Must total 100.</p>
        <div className="space-y-3">
          {['recency', 'frequency', 'sentiment', 'commitment', 'response'].map((key) => (
            <div key={key} className="flex items-center gap-4">
              <label className="w-28 text-sm text-text-secondary capitalize">{key}</label>
              <input
                type="range"
                min={0}
                max={50}
                value={weights[key] || 0}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    health_weights: { ...weights, [key]: parseInt(e.target.value) },
                  })
                }
                className="flex-1 accent-gold"
              />
              <span className="w-10 text-right text-sm text-text-primary font-medium">
                {weights[key]}%
              </span>
            </div>
          ))}
        </div>
        {Object.values(weights).reduce((a, b) => a + b, 0) !== 100 && (
          <p className="text-xs text-amber-400">
            Weights total {Object.values(weights).reduce((a, b) => a + b, 0)}% — should be 100%.
          </p>
        )}
      </section>

      {/* Save Button */}
      <div className="flex items-center gap-3">
        <button
          onClick={save}
          disabled={saving}
          className="bg-gold hover:bg-gold/90 text-midnight px-6 py-2 rounded-lg text-sm font-medium disabled:opacity-40"
        >
          {saving ? 'Saving...' : 'Save Settings'}
        </button>
        {saved && <span className="text-sm text-green-400">Saved</span>}
      </div>

      {/* Data Management */}
      <section className="bg-surface rounded-xl border border-red-500/20 p-6 space-y-4">
        <h2 className="font-heading text-lg font-semibold text-red-400 flex items-center gap-2">
          <ExclamationTriangleIcon className="w-5 h-5" />
          Data Management
        </h2>
        <p className="text-sm text-text-muted">
          Permanently delete all CRM data. Settings will be preserved. This cannot be undone.
        </p>
        {!showDeleteConfirm ? (
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 px-4 py-2 rounded-lg text-sm font-medium"
          >
            Delete All Data
          </button>
        ) : (
          <div className="flex items-center gap-3">
            <button
              onClick={deleteAllData}
              className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium"
            >
              Confirm Delete Everything
            </button>
            <button
              onClick={() => setShowDeleteConfirm(false)}
              className="text-sm text-text-muted hover:text-text-primary"
            >
              Cancel
            </button>
          </div>
        )}
        {deleteResult && (
          <div className="bg-surface-light rounded-lg p-4">
            <p className="text-sm text-text-primary font-medium">{deleteResult.detail}</p>
            <p className="text-xs text-text-muted mt-1">
              Total deleted: {deleteResult.total_deleted} records
            </p>
          </div>
        )}
      </section>
    </div>
  );
}
