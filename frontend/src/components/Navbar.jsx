/**
 * Navigation bar component.
 * Shows app name, navigation links, and user info.
 */
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const navLinks = [
  { to: '/dashboard', label: 'Dashboard', icon: '📊' },
  { to: '/chat', label: 'AI Assistant', icon: '🤖' },
  { to: '/approvals', label: 'Approvals', icon: '✅' },
  { to: '/budgets', label: 'Budgets', icon: '💰' },
  { to: '/policies', label: 'Policies', icon: '🛡️' },
  { to: '/transactions', label: 'Transactions', icon: '📋' },
  { to: '/audit', label: 'Audit Log', icon: '🔍' },
];

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAuthenticated) return null;

  return (
    <nav className="bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/dashboard" className="flex items-center gap-2 no-underline">
            <span className="text-2xl">🚀</span>
            <span className="text-xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              PayPilot AI
            </span>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`px-3 py-2 rounded-lg text-sm font-medium no-underline transition-colors ${
                  location.pathname === link.to
                    ? 'bg-indigo-50 text-indigo-700'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                <span className="mr-1">{link.icon}</span>
                {link.label}
              </Link>
            ))}
          </div>

          {/* User Info & Logout */}
          <div className="flex items-center gap-3">
            <span className="text-sm text-slate-600 hidden sm:inline">
              👤 {user?.name || 'User'}
            </span>
            <button
              onClick={handleLogout}
              className="px-3 py-1.5 text-sm font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors cursor-pointer border-none"
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <div className="md:hidden border-t border-slate-100 px-2 py-2 flex flex-wrap gap-1">
        {navLinks.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className={`px-2 py-1 rounded text-xs font-medium no-underline ${
              location.pathname === link.to
                ? 'bg-indigo-50 text-indigo-700'
                : 'text-slate-500 hover:bg-slate-50'
            }`}
          >
            {link.icon} {link.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}
