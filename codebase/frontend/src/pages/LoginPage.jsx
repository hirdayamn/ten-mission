import { useState, useEffect } from 'react';
import { Mail, Lock, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components';
import { api } from '../api/client';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();

  // If already logged in with a valid token, redirect to dashboard
  useEffect(() => {
    if (!api.isTokenExpired() && localStorage.getItem('accessToken')) {
      navigate('/action');
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email) return;

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      addToast('Please enter a valid email address', 'error');
      return;
    }

    setLoading(true);
    try {
      await login(email);
      addToast('Logged in successfully!');
      navigate('/action');
    } catch (error) {
      addToast(error.message || 'Login failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">TenMission</h1>
          <p className="text-gray-600 mt-2">Sign in to manage your bookings</p>
        </div>

        <form onSubmit={handleSubmit} className="card p-8">
          <div className="mb-6">
            <label htmlFor="email" className="label">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="input pl-10"
                disabled={loading}
                autoComplete="email"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || !email}
            className="btn-primary w-full"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Signing in...
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                Sign In
                <ArrowRight className="w-5 h-5" />
              </span>
            )}
          </button>

        </form>
      </div>
    </div>
  );
}