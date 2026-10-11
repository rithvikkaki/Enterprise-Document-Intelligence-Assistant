import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { Lock, Mail, Eye, EyeOff, AlertCircle, Layers } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../api/auth';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loginMutation = useMutation({
    mutationFn: authApi.login,
    onSuccess: async (tokens) => {
      setErrorMessage(null);
      await login(tokens.access_token, tokens.refresh_token);
      navigate('/org-select');
    },
    onError: (err: any) => {
      if (err.response?.status === 401) {
        setErrorMessage('Invalid email or password. Please try again.');
      } else if (err.response?.data?.error?.message) {
        setErrorMessage(err.response.data.error.message);
      } else {
        setErrorMessage('Failed to connect to the server. Please ensure the backend is running.');
      }
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setErrorMessage('Please provide both email and password.');
      return;
    }
    setErrorMessage(null);
    loginMutation.mutate({ email, password });
  };

  return (
    <div className="min-h-screen bg-[#fafafa] flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-red-600 text-white shadow-xs mb-3">
          <Layers size={22} strokeWidth={2.2} />
        </div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">
          Welcome back
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          Sign in to access your enterprise document intelligence workspace
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow-card border border-slate-200/90 rounded-2xl sm:px-10">
          {errorMessage && (
            <div className="mb-4 p-3 rounded-xl bg-rose-50 border border-rose-200 flex items-center gap-2.5 text-sm text-rose-700">
              <AlertCircle size={16} className="shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Work Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Mail size={16} />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@enterprise.com"
                  className="block w-full pl-10 pr-3 py-2.5 bg-white border border-slate-200 rounded-xl text-sm placeholder-slate-400 text-slate-900 focus:outline-none focus:border-red-500 focus:ring-4 focus:ring-red-500/10 transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock size={16} />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="block w-full pl-10 pr-10 py-2.5 bg-white border border-slate-200 rounded-xl text-sm placeholder-slate-400 text-slate-900 focus:outline-none focus:border-red-500 focus:ring-4 focus:ring-red-500/10 transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loginMutation.isPending}
              className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-xl shadow-xs text-sm font-semibold text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-4 focus:ring-red-500/20 disabled:opacity-50 transition-colors cursor-pointer"
            >
              {loginMutation.isPending ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 border-t border-slate-100 pt-4 text-center">
            <p className="text-sm text-slate-500">
              Don't have an account?{' '}
              <Link to="/register" className="font-semibold text-red-600 hover:text-red-700">
                Register here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
