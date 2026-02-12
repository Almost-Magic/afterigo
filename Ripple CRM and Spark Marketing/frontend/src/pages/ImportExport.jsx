import { useState } from 'react';
import {
  ArrowUpTrayIcon,
  ArrowDownTrayIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

function FileUploader({ label, endpoint, onResult }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [importing, setImporting] = useState(false);
  const [error, setError] = useState(null);
  const [importResult, setImportResult] = useState(null);

  const doPreview = async (f) => {
    if (!f) return;
    setLoading(true);
    setError(null);
    setPreview(null);
    setImportResult(null);
    const form = new FormData();
    form.append('file', f);
    try {
      const res = await fetch(`/api/import-export/import/${endpoint}?commit=false`, {
        method: 'POST',
        body: form,
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Error ${res.status}`);
      }
      setPreview(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const doImport = async () => {
    if (!file) return;
    setImporting(true);
    setError(null);
    const form = new FormData();
    form.append('file', file);
    try {
      const res = await fetch(`/api/import-export/import/${endpoint}?commit=true`, {
        method: 'POST',
        body: form,
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Error ${res.status}`);
      }
      const result = await res.json();
      setImportResult(result);
      setPreview(null);
      if (onResult) onResult(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <label className="flex-1">
          <div className="flex items-center gap-2 bg-surface-light border border-dashed border-border rounded-lg p-4 cursor-pointer hover:border-gold/50 transition-colors">
            <ArrowUpTrayIcon className="w-5 h-5 text-text-muted" />
            <span className="text-sm text-text-secondary">
              {file ? file.name : `Choose ${label} CSV file...`}
            </span>
          </div>
          <input
            type="file"
            accept=".csv"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              setFile(f);
              setPreview(null);
              setImportResult(null);
              if (f) doPreview(f);
            }}
          />
        </label>
      </div>

      {loading && <p className="text-sm text-text-muted">Analysing CSV...</p>}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-sm text-red-400">{error}</div>
      )}

      {preview && (
        <div className="space-y-3">
          <div className="flex items-center gap-4 text-sm">
            <span className="text-text-muted">Total rows: <b className="text-text-primary">{preview.total_rows}</b></span>
            <span className="text-green-400">To import: <b>{preview.to_import}</b></span>
            <span className="text-amber-400">Duplicates: <b>{preview.duplicates}</b></span>
            <span className="text-text-muted">Fields: {preview.mapped_fields.join(', ')}</span>
          </div>

          <div className="max-h-64 overflow-y-auto border border-border rounded-lg">
            <table className="w-full text-xs">
              <thead className="bg-surface-light sticky top-0">
                <tr>
                  <th className="px-3 py-2 text-left text-text-muted">Status</th>
                  {preview.mapped_fields.map((f) => (
                    <th key={f} className="px-3 py-2 text-left text-text-muted capitalize">{f.replace('_', ' ')}</th>
                  ))}
                  <th className="px-3 py-2 text-left text-text-muted">Note</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {preview.rows.map((row, i) => (
                  <tr
                    key={i}
                    className={row.is_duplicate ? 'bg-amber-500/5' : ''}
                  >
                    <td className="px-3 py-1.5">
                      {row.is_duplicate ? (
                        <ExclamationTriangleIcon className="w-4 h-4 text-amber-400" />
                      ) : (
                        <CheckCircleIcon className="w-4 h-4 text-green-400" />
                      )}
                    </td>
                    {preview.mapped_fields.map((f) => (
                      <td key={f} className="px-3 py-1.5 text-text-primary">{row.row_data[f] || ''}</td>
                    ))}
                    <td className="px-3 py-1.5 text-text-muted">{row.duplicate_reason || ''}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {preview.to_import > 0 && (
            <button
              onClick={doImport}
              disabled={importing}
              className="bg-gold hover:bg-gold/90 text-midnight px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-40"
            >
              {importing ? 'Importing...' : `Import ${preview.to_import} records`}
            </button>
          )}
        </div>
      )}

      {importResult && (
        <div className="bg-green-400/10 border border-green-400/30 rounded-lg p-4 flex items-center gap-3">
          <CheckCircleIcon className="w-5 h-5 text-green-400" />
          <span className="text-sm text-green-400">
            Successfully imported {importResult.imported} records ({importResult.duplicates} duplicates skipped)
          </span>
        </div>
      )}
    </div>
  );
}

export default function ImportExport() {
  const [tab, setTab] = useState('import');

  const exportFile = (type) => {
    window.open(`/api/import-export/export/${type}`, '_blank');
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <DocumentTextIcon className="w-7 h-7 text-gold" />
        <div>
          <h1 className="font-heading text-2xl font-semibold text-text-primary">Import / Export</h1>
          <p className="text-sm text-text-muted">Bring data in or take it out — your data, your way</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-surface rounded-lg p-1 border border-border w-fit">
        {[
          { key: 'import', label: 'Import' },
          { key: 'export', label: 'Export' },
        ].map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              tab === t.key
                ? 'bg-gold/10 text-gold'
                : 'text-text-secondary hover:text-text-primary hover:bg-surface-light'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'import' && (
        <div className="space-y-8">
          <div className="bg-surface rounded-xl border border-border p-6 space-y-4">
            <h2 className="font-heading text-lg font-semibold text-text-primary flex items-center gap-2">
              <ArrowUpTrayIcon className="w-5 h-5" /> Import Contacts
            </h2>
            <p className="text-xs text-text-muted">
              Accepted headers: first_name, last_name, email, phone, role, type, source, company_name
            </p>
            <FileUploader label="contacts" endpoint="contacts" />
          </div>

          <div className="bg-surface rounded-xl border border-border p-6 space-y-4">
            <h2 className="font-heading text-lg font-semibold text-text-primary flex items-center gap-2">
              <ArrowUpTrayIcon className="w-5 h-5" /> Import Companies
            </h2>
            <p className="text-xs text-text-muted">
              Accepted headers: name (or Company Name), industry, website, address
            </p>
            <FileUploader label="companies" endpoint="companies" />
          </div>
        </div>
      )}

      {tab === 'export' && (
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-surface rounded-xl border border-border p-6 space-y-4">
            <h2 className="font-heading text-lg font-semibold text-text-primary flex items-center gap-2">
              <ArrowDownTrayIcon className="w-5 h-5" /> Export Contacts
            </h2>
            <p className="text-sm text-text-muted">Download all contacts as a CSV file.</p>
            <button
              onClick={() => exportFile('contacts')}
              className="bg-gold hover:bg-gold/90 text-midnight px-4 py-2 rounded-lg text-sm font-medium"
            >
              Download Contacts CSV
            </button>
          </div>

          <div className="bg-surface rounded-xl border border-border p-6 space-y-4">
            <h2 className="font-heading text-lg font-semibold text-text-primary flex items-center gap-2">
              <ArrowDownTrayIcon className="w-5 h-5" /> Export Deals
            </h2>
            <p className="text-sm text-text-muted">Download all deals as a CSV file.</p>
            <button
              onClick={() => exportFile('deals')}
              className="bg-gold hover:bg-gold/90 text-midnight px-4 py-2 rounded-lg text-sm font-medium"
            >
              Download Deals CSV
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
