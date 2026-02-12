import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { toast } from '../components/Toast';

export default function Contacts() {
  const [contacts, setContacts] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const navigate = useNavigate();
  const limit = 25;

  useEffect(() => {
    api.get(`/contacts?limit=${limit}&offset=${page * limit}`)
      .then((d) => { setContacts(d.items); setTotal(d.total); })
      .catch((e) => toast(e.message, 'error'));
  }, [page]);

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold font-heading">Contacts</h2>
        <span className="text-sm text-text-muted">{total} contacts</span>
      </div>

      <div className="bg-surface border border-border rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-text-muted text-xs">
              <th className="text-left p-3 font-medium">Name</th>
              <th className="text-left p-3 font-medium">Email</th>
              <th className="text-left p-3 font-medium">Company</th>
              <th className="text-right p-3 font-medium">Touchpoints</th>
              <th className="text-right p-3 font-medium">Identified</th>
            </tr>
          </thead>
          <tbody>
            {contacts.map((c) => (
              <tr
                key={c.id}
                onClick={() => navigate(`/contacts/${c.id}`)}
                className="border-b border-border/50 hover:bg-surface-light/50 cursor-pointer transition-colors"
              >
                <td className="p-3 text-text-primary font-medium">{c.name || 'Anonymous'}</td>
                <td className="p-3 text-text-secondary">{c.email || '-'}</td>
                <td className="p-3 text-text-secondary">{c.company || '-'}</td>
                <td className="p-3 text-right text-gold font-mono">{c.touchpoint_count}</td>
                <td className="p-3 text-right text-text-muted text-xs">
                  {c.identified_at ? new Date(c.identified_at).toLocaleDateString() : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {contacts.length === 0 && (
          <p className="text-center text-text-muted py-8">No contacts yet.</p>
        )}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="px-3 py-1 text-sm bg-surface-light border border-border rounded-lg text-text-secondary hover:text-text-primary disabled:opacity-30"
          >
            Prev
          </button>
          <span className="text-sm text-text-muted">
            Page {page + 1} of {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1}
            className="px-3 py-1 text-sm bg-surface-light border border-border rounded-lg text-text-secondary hover:text-text-primary disabled:opacity-30"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
