import { useEffect, useState } from 'react';

let toastFn = null;

export function toast(message, type = 'success') {
  if (toastFn) toastFn({ message, type, id: Date.now() });
}

export default function ToastContainer() {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    toastFn = (t) => {
      setToasts((prev) => [...prev, t]);
      setTimeout(() => setToasts((prev) => prev.filter((x) => x.id !== t.id)), 3000);
    };
    return () => { toastFn = null; };
  }, []);

  return (
    <div className="fixed top-4 right-4 z-[100] flex flex-col gap-2">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`px-4 py-2.5 rounded-lg text-sm font-medium shadow-lg transition-all animate-[slideIn_0.2s_ease-out] ${
            t.type === 'success' ? 'bg-healthy/20 text-healthy border border-healthy/30' :
            t.type === 'error' ? 'bg-critical/20 text-critical border border-critical/30' :
            'bg-warning/20 text-warning border border-warning/30'
          }`}
        >
          {t.message}
        </div>
      ))}
    </div>
  );
}
