/**
 * Navigation bar component with Blue, Grey, and Orange design system.
 */
import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { paymentRequestAPI } from '../services/api';

const navLinks = [
  { to: '/dashboard', label: 'Dashboard', icon: '📊' },
  { to: '/chat', label: 'Universal Marketplace', icon: '🛍️' },
  { to: '/approvals', label: 'Approvals', icon: '✅', hasBadge: true },
  { to: '/budgets', label: 'Budgets', icon: '💰' },
  { to: '/policies', label: 'Policies', icon: '🛡️' },
  { to: '/transactions', label: 'Transactions', icon: '📋' },
  { to: '/audit', label: 'Audit Log', icon: '🔍' },
];

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [pendingCount, setPendingCount] = useState(0);

  useEffect(() => {
    if (!isAuthenticated) return;
    const fetchPending = async () => {
      try {
        const res = await paymentRequestAPI.list('PENDING_APPROVAL');
        setPendingCount(res.data?.length || 0);
      } catch (e) {
        // quiet error
      }
    };
    fetchPending();
    const interval = setInterval(fetchPending, 10000);
    return () => clearInterval(interval);
  }, [isAuthenticated, location.pathname]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAuthenticated) return null;

  return (
    <nav className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <Link to="/dashboard" className="flex items-center gap-2.5 no-underline group">
            <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-sm shadow-blue-500/20 group-hover:bg-blue-700 transition">
              <span className="text-xl">🚀</span>
            </div>
            <div className="flex flex-col">
              <span className="text-lg font-bold text-slate-900 tracking-tight flex items-center gap-1.5">
                PayPilot <span className="text-blue-600">AI</span>
                <span className="text-[10px] uppercase font-semibold bg-orange-100 text-orange-700 px-1.5 py-0.5 rounded tracking-wide">
                  Secured
                </span>
              </span>
              <span className="text-[11px] text-slate-500 font-medium">Policy-Driven Agent Checkout</span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <div className="hidden lg:flex items-center gap-1">
            {navLinks.map((link) => {
              const isActive = location.pathname === link.to;
              return (
                <Link
                  key={link.to}
                  to={link.to}
                  className={`px-3.5 py-2 rounded-lg text-sm font-medium no-underline transition-all flex items-center gap-1.5 relative ${
                    isActive
                      ? 'bg-blue-50 text-blue-700 font-semibold'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                  }`}
                >
                  <span className="text-base">{link.icon}</span>
                  {link.label}
                  {link.hasBadge && pendingCount > 0 && (
                    <span className="ml-1 px-1.5 py-0.5 text-xs font-bold bg-orange-500 text-white rounded-full animate-pulse shadow-xs">
                      {pendingCount}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>

          {/* User Profile & Logout */}
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 bg-slate-50 border border-slate-200/80 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-700">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
              <span>{user?.name || user?.email || 'User'}</span>
            </div>
            <button
              onClick={handleLogout}
              className="px-3 py-1.5 text-xs font-medium text-slate-600 bg-slate-100 rounded-lg hover:bg-red-50 hover:text-red-600 transition border border-transparent cursor-pointer"
            >
              Sign out
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Nav */}
      <div className="lg:hidden border-t border-slate-100 px-3 py-2 flex items-center justify-between overflow-x-auto gap-2 bg-slate-50/50">
        {navLinks.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className={`px-2.5 py-1.5 rounded-md text-xs font-medium no-underline whitespace-nowrap flex items-center gap-1 ${
              location.pathname === link.to
                ? 'bg-blue-600 text-white'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <span>{link.icon}</span>
            <span>{link.label}</span>
            {link.hasBadge && pendingCount > 0 && (
              <span className="bg-orange-500 text-white px-1.5 py-0.2 rounded-full text-[10px]">
                {pendingCount}
              </span>
            )}
          </Link>
        ))}
      </div>
    </nav>
  );
}
