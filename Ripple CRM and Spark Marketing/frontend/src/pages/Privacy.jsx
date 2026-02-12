import { useEffect, useState } from 'react';
import {
  ShieldCheckIcon,
  DocumentArrowDownIcon,
  MagnifyingGlassIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';

function ConsentBadge({ granted }) {
  return granted ? (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-green-400/10 text-green-400">
      <CheckCircleIcon className="w-3.5 h-3.5" /> Granted
    </span>
  ) : (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-400/10 text-red-400">
      <XCircleIcon className="w-3.5 h-3.5" /> Revoked
    </span>
  );
}

export default function Privacy() {
  const [tab, setTab] = useState('dsar');
  const [contactId, setContactId] = useState('');
  const [report, setReport] = useState(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [reportError, setReportError] = useState(null);

  const [consents, setConsents] = useState([]);
  const [consentLoading, setConsentLoading] = useState(false);
  const [consentTotal, setConsentTotal] = useState(0);

  const [contacts, setContacts] = useState([]);

  // Load contacts for the dropdown
  useEffect(() => {
    fetch('/api/contacts?page_size=200')
      .then((r) => r.json())
      .then((d) => setContacts(d.items || []))
      .catch(() => {});
  }, []);

  // Load consents
  const fetchConsents = async () => {
    setConsentLoading(true);
    try {
      const res = await fetch('/api/privacy/consents?page_size=100');
      if (!res.ok) throw new Error(`${res.status}`);
      const d = await res.json();
      setConsents(d.items || []);
      setConsentTotal(d.total || 0);
    } catch {
      /* ignore */
    } finally {
      setConsentLoading(false);
    }
  };

  useEffect(() => {
    if (tab === 'consents') fetchConsents();
  }, [tab]);

  const generateReport = async () => {
    if (!contactId) return;
    setReportLoading(true);
    setReportError(null);
    setReport(null);
    try {
      const res = await fetch(`/api/privacy/contacts/${contactId}/report`);
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `${res.status}`);
      }
      setReport(await res.json());
    } catch (e) {
      setReportError(e.message);
    } finally {
      setReportLoading(false);
    }
  };

  const recordConsent = async (e) => {
    e.preventDefault();
    const form = new FormData(e.target);
    const payload = {
      contact_id: form.get('contact_id'),
      consent_type: form.get('consent_type'),
      granted: form.get('granted') === 'true',
      source: form.get('source') || 'manual',
    };
    if (!payload.contact_id || !payload.consent_type) return;
    try {
      const res = await fetch('/api/privacy/consents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        e.target.reset();
        fetchConsents();
      }
    } catch {
      /* ignore */
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <ShieldCheckIcon className="w-7 h-7 text-gold" />
        <div>
          <h1 className="font-heading text-2xl font-semibold text-text-primary">Transparency Portal</h1>
          <p className="text-sm text-text-muted">Privacy management, DSAR reports, and consent tracking</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-surface rounded-lg p-1 border border-border w-fit">
        {[
          { key: 'dsar', label: 'DSAR Report' },
          { key: 'consents', label: 'Consent Log' },
          { key: 'record', label: 'Record Consent' },
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

      {/* DSAR Report Tab */}
      {tab === 'dsar' && (
        <div className="bg-surface rounded-xl border border-border p-6 space-y-6">
          <div>
            <h2 className="font-heading text-lg font-semibold text-text-primary mb-1">
              Data Subject Access Request
            </h2>
            <p className="text-sm text-text-muted">
              Generate a complete report of all data held about a contact.
            </p>
          </div>

          <div className="flex gap-3 items-end">
            <div className="flex-1">
              <label className="block text-sm text-text-secondary mb-1">Select Contact</label>
              <select
                value={contactId}
                onChange={(e) => setContactId(e.target.value)}
                className="w-full bg-surface-light border border-border rounded-lg px-3 py-2 text-sm text-text-primary"
              >
                <option value="">Choose a contact...</option>
                {contacts.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.first_name} {c.last_name} {c.email ? `(${c.email})` : ''}
                  </option>
                ))}
              </select>
            </div>
            <button
              onClick={generateReport}
              disabled={!contactId || reportLoading}
              className="bg-gold hover:bg-gold/90 text-midnight px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-40 flex items-center gap-2"
            >
              {reportLoading ? (
                <ArrowPathIcon className="w-4 h-4 animate-spin" />
              ) : (
                <DocumentArrowDownIcon className="w-4 h-4" />
              )}
              Generate Report
            </button>
          </div>

          {reportError && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
              <p className="text-red-400 text-sm">{reportError}</p>
            </div>
          )}

          {report && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="font-heading font-semibold text-text-primary">
                  DSAR Report — {report.contact.first_name} {report.contact.last_name}
                </h3>
                <span className="text-xs text-text-muted">
                  Generated {new Date(report.report_generated_at).toLocaleString('en-AU')}
                </span>
              </div>

              {/* Contact Details */}
              <div className="bg-surface-light rounded-lg p-4">
                <h4 className="text-sm font-medium text-text-primary mb-2">Personal Data</h4>
                <dl className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
                  {Object.entries(report.contact)
                    .filter(([k]) => k !== 'id')
                    .map(([k, v]) => (
                      <div key={k} className="flex justify-between">
                        <dt className="text-text-muted capitalize">{k.replace('_', ' ')}</dt>
                        <dd className="text-text-primary">{v || '—'}</dd>
                      </div>
                    ))}
                </dl>
              </div>

              {/* Summary Stats */}
              <div className="grid grid-cols-3 gap-4">
                {[
                  { label: 'Interactions', val: report.total_interactions },
                  { label: 'Notes', val: report.total_notes },
                  { label: 'Commitments', val: report.total_commitments },
                ].map((s) => (
                  <div key={s.label} className="bg-surface-light rounded-lg p-4 text-center">
                    <p className="text-2xl font-heading font-semibold text-text-primary">{s.val}</p>
                    <p className="text-xs text-text-muted">{s.label}</p>
                  </div>
                ))}
              </div>

              {/* Interactions List */}
              {report.interactions.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-text-primary mb-2">Interactions ({report.interactions.length})</h4>
                  <div className="divide-y divide-border bg-surface-light rounded-lg overflow-hidden">
                    {report.interactions.map((i) => (
                      <div key={i.id} className="px-4 py-2 text-sm flex items-center justify-between">
                        <div>
                          <span className="font-medium text-text-primary">{i.subject}</span>
                          <span className="text-text-muted ml-2">({i.type})</span>
                        </div>
                        <span className="text-xs text-text-muted">
                          {i.occurred_at ? new Date(i.occurred_at).toLocaleDateString('en-AU') : '—'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Notes */}
              {report.notes.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-text-primary mb-2">Notes ({report.notes.length})</h4>
                  <div className="space-y-2">
                    {report.notes.map((n) => (
                      <div key={n.id} className="bg-surface-light rounded-lg p-3 text-sm">
                        <p className="text-text-primary">{n.content}</p>
                        <p className="text-xs text-text-muted mt-1">
                          {n.created_at ? new Date(n.created_at).toLocaleDateString('en-AU') : '—'}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Commitments */}
              {report.commitments.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-text-primary mb-2">Commitments ({report.commitments.length})</h4>
                  <div className="divide-y divide-border bg-surface-light rounded-lg overflow-hidden">
                    {report.commitments.map((c) => (
                      <div key={c.id} className="px-4 py-2 text-sm flex items-center justify-between">
                        <div>
                          <span className="font-medium text-text-primary">{c.description}</span>
                          <span className="text-text-muted ml-2">({c.committed_by})</span>
                        </div>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          c.status === 'fulfilled' ? 'bg-green-400/10 text-green-400' :
                          c.status === 'broken' ? 'bg-red-400/10 text-red-400' :
                          'bg-amber-400/10 text-amber-400'
                        }`}>
                          {c.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Consents */}
              {report.consents.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-text-primary mb-2">Consent Records ({report.consents.length})</h4>
                  <div className="divide-y divide-border bg-surface-light rounded-lg overflow-hidden">
                    {report.consents.map((c) => (
                      <div key={c.id} className="px-4 py-2 text-sm flex items-center justify-between">
                        <div>
                          <span className="font-medium text-text-primary">{c.consent_type}</span>
                          <span className="text-text-muted ml-2">via {c.source || 'unknown'}</span>
                        </div>
                        <ConsentBadge granted={c.granted} />
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Consent Log Tab */}
      {tab === 'consents' && (
        <div className="bg-surface rounded-xl border border-border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-heading text-lg font-semibold text-text-primary">
              Consent Log
              <span className="text-sm text-text-muted font-normal ml-2">({consentTotal} records)</span>
            </h2>
            <button
              onClick={fetchConsents}
              className="p-2 rounded-lg hover:bg-surface-light text-text-muted hover:text-text-primary"
            >
              <ArrowPathIcon className={`w-4 h-4 ${consentLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>

          {consents.length === 0 ? (
            <p className="text-sm text-text-muted text-center py-8">No consent records yet</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-text-muted border-b border-border">
                    <th className="pb-2 font-medium">Contact</th>
                    <th className="pb-2 font-medium">Type</th>
                    <th className="pb-2 font-medium">Status</th>
                    <th className="pb-2 font-medium">Source</th>
                    <th className="pb-2 font-medium">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {consents.map((c) => {
                    const contact = contacts.find((ct) => ct.id === c.contact_id);
                    return (
                      <tr key={c.id} className="text-text-primary">
                        <td className="py-2">
                          {contact ? `${contact.first_name} ${contact.last_name}` : c.contact_id.slice(0, 8)}
                        </td>
                        <td className="py-2">{c.consent_type}</td>
                        <td className="py-2"><ConsentBadge granted={c.granted} /></td>
                        <td className="py-2 text-text-muted">{c.source || '—'}</td>
                        <td className="py-2 text-text-muted">
                          {c.created_at ? new Date(c.created_at).toLocaleDateString('en-AU') : '—'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Record Consent Tab */}
      {tab === 'record' && (
        <div className="bg-surface rounded-xl border border-border p-6 max-w-lg">
          <h2 className="font-heading text-lg font-semibold text-text-primary mb-4">Record New Consent</h2>
          <form onSubmit={recordConsent} className="space-y-4">
            <div>
              <label className="block text-sm text-text-secondary mb-1">Contact</label>
              <select
                name="contact_id"
                required
                className="w-full bg-surface-light border border-border rounded-lg px-3 py-2 text-sm text-text-primary"
              >
                <option value="">Choose a contact...</option>
                {contacts.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.first_name} {c.last_name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-text-secondary mb-1">Consent Type</label>
              <select
                name="consent_type"
                required
                className="w-full bg-surface-light border border-border rounded-lg px-3 py-2 text-sm text-text-primary"
              >
                <option value="">Select type...</option>
                <option value="email_marketing">Email Marketing</option>
                <option value="data_processing">Data Processing</option>
                <option value="third_party_sharing">Third Party Sharing</option>
                <option value="analytics">Analytics</option>
                <option value="profiling">Profiling</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-text-secondary mb-1">Status</label>
              <select
                name="granted"
                required
                className="w-full bg-surface-light border border-border rounded-lg px-3 py-2 text-sm text-text-primary"
              >
                <option value="true">Granted</option>
                <option value="false">Revoked</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-text-secondary mb-1">Source</label>
              <input
                name="source"
                placeholder="e.g. email, phone, in-person"
                className="w-full bg-surface-light border border-border rounded-lg px-3 py-2 text-sm text-text-primary"
              />
            </div>
            <button
              type="submit"
              className="bg-gold hover:bg-gold/90 text-midnight px-4 py-2 rounded-lg text-sm font-medium"
            >
              Record Consent
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
