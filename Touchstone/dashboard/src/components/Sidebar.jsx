import { NavLink } from 'react-router-dom';
import {
  ChartBarIcon,
  MegaphoneIcon,
  ArrowsRightLeftIcon,
  UsersIcon,
} from '@heroicons/react/24/outline';

const NAV = [
  { to: '/', label: 'Overview', icon: ChartBarIcon },
  { to: '/campaigns', label: 'Campaigns', icon: MegaphoneIcon },
  { to: '/compare', label: 'Model Comparison', icon: ArrowsRightLeftIcon },
  { to: '/contacts', label: 'Contacts', icon: UsersIcon },
];

export default function Sidebar() {
  return (
    <aside className="w-56 bg-surface dark:bg-surface border-r border-border flex flex-col shrink-0">
      <div className="p-4 border-b border-border">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gold/20 flex items-center justify-center text-gold font-bold text-sm">
            T
          </div>
          <div>
            <h1 className="text-sm font-semibold text-text-primary font-heading">Touchstone</h1>
            <p className="text-[10px] text-text-muted">Marketing Attribution</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-3 space-y-0.5">
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'bg-gold/15 text-gold font-medium'
                  : 'text-text-secondary hover:bg-surface-light hover:text-text-primary'
              }`
            }
          >
            <Icon className="w-4.5 h-4.5" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="p-3 border-t border-border">
        <p className="text-[10px] text-text-muted text-center">
          Almost Magic Tech Lab
        </p>
      </div>
    </aside>
  );
}
