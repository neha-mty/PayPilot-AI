/**
 * Navigation bar component with exact brand palette:
 * Deep Ocean Blue: #022E51
 * Steel Blue Grey: #A3B4C8
 * Burnt Orange: #CC6D3D
 * Deep Burnt Orange: #B74803
 */
import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { paymentRequestAPI } from '../services/api';

const navLinks = [
  { to: '/dashboard', label: 'Dashboard', icon: '📊' },
  { to: '/chat', label: 'Universal Search', icon: '🔍' },
  { to: '/approvals', label: 'Approvals', icon: '✅', hasBadge: true },
  { to: '/budgets', label: 'Budgets', icon: '💰' },
  { to: '/policies', label: 'Policies', icon: '🛡️' },
  { to: '/transactions', label: 'Transactions', icon: '📋' },
  { to: '/audit', label: 'Audit Log', icon: '📝' },
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
        // silence background refresh
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
    <nav className="bg-[#022E51] border-b border-[#011E36] sticky top-0 z-50 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <Link to="/dashboard" className="flex items-center gap-3 no-underline group">
            <div className="w-10 h-10 rounded-xl bg-[#CC6D3D] flex items-center justify-center text-white shadow-sm group-hover:bg-[#B74803] transition">
              <span className="text-xl">🚀</span>
            </div>
            <div className="flex flex-col">
              <span className="text-lg font-extrabold text-white tracking-tight flex items-center gap-2">
                PayPilot <span className="text-[#A3B4C8]">AI</span>
                <span className="text-[10px] uppercase font-bold bg-[#CC6D3D]/30 border border-[#CC6D3D]/50 text-white px-2 py-0.5 rounded">
                  Search Engine
                </span>
              </span>
              <span className="text-[11px] text-[#A3B4C8] font-medium">Internet Discovery & Policy Authorization</span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <div className="hidden lg:flex items-center gap-1.5">
            {navLinks.map((link) => {
              const isActive = location.pathname === link.to;
              return (
                <Link
                  key={link.to}
                  to={link.to}
                  className={`px-3.5 py-2 rounded-xl text-xs font-bold no-underline transition-all flex items-center gap-1.5 relative ${
                    isActive
                      ? 'bg-white/10 text-white shadow-inner border border-white/20'
                      : 'text-[#A3B4C8] hover:bg-white/5 hover:text-white'
                  }`}
                >
                  <span className="text-sm">{link.icon}</span>
                  {link.label}
                  {link.hasBadge && pendingCount > 0 && (
                    <span className="ml-1 px-1.5 py-0.2 text-[10px] font-black bg-[#CC6D3D] text-white rounded-full animate-pulse shadow-sm">
                      {pendingCount}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>

          {/* User Profile & Logout */}
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 bg-white/10 border border-white/15 px-3 py-1.5 rounded-xl text-xs font-medium text-white">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
              <span>{user?.name || user?.email || 'User'}</span>
            </div>
            <button
              onClick={handleLogout}
              className="px-3 py-1.5 text-xs font-bold text-white bg-white/10 border border-white/20 rounded-xl hover:bg-[#B74803] transition cursor-pointer"
            >
              Sign out
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Nav */}
      <div className="lg:hidden border-t border-[#011E36] px-3 py-2 flex items-center justify-between overflow-x-auto gap-2 bg-[#022E51]">
        {navLinks.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className={`px-2.5 py-1.5 rounded-lg text-xs font-semibold no-underline whitespace-nowrap flex items-center gap-1 ${
              location.pathname === link.to
                ? 'bg-[#CC6D3D] text-white'
                : 'text-[#A3B4C8] hover:bg-white/5'
            }`}
          >
            <span>{link.icon}</span>
            <span>{link.label}</span>
            {link.hasBadge && pendingCount > 0 && (
              <span className="bg-[#B74803] text-white px-1.5 py-0.2 rounded-full text-[10px]">
                {pendingCount}
              </span>
            )}
          </Link>
        ))}
      </div>
    </nav>
  );
}
