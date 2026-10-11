import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { User as UserIcon, Lock, Mail, AlertCircle, CheckCircle2, Layers } from 'lucide-react';
import { authApi } from '../api/auth';

export default function RegisterPage() {
  const navigate = useNavigate();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);

  const registerMutation = useMutation({
    mutationFn: authApi.register,
    onSuccess: () => {
      setIsSuccess(true);
      setTimeout(() => navigate('/login'), 1500);
    },
    onError: (err: any) => {
      if (err.response?.data?.error?.message) {
        setErrorMessage(err.response.data.error.message);
      } else {
        setErrorMessage('Registration failed. Please check your details and try again.');
      }
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (password.length < 8) {
      setErrorMessage('Password must be at least 8 characters long.');
      return;
    }
    if (password !== confirmPassword) {
      setErrorMessage('Passwords do not match.');
      return;
    }
    setErrorMessage(null);
    registerMutation.mutate({ full_name: fullName, email, password });
  };

  return (
    <div className="min-h-screen bg-[#fafafa] flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-red-600 text-white shadow-xs mb-3">
          <Layers size={22} strokeWidth={2.2} />
        </div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">
          Create an Account
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          Get started with local-first secure document intelligence
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow-card border border-slate-200/90 rounded-2xl sm:px-10">
          {isSuccess && (
            <div className="mb-4 p-3 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center gap-2 text-sm text-emerald-700">
              <CheckCircle2 size={16} className="shrink-0" />
              <span>Registration successful! Redirecting to login...</span>
            </div>
          )}

          {errorMessage && (
            <div className="mb-4 p-3 rounded-xl bg-rose-50 border border-rose-200 flex items-center gap-2 text-sm text-rose-700">
              <AlertCircle size={16} className="shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Full Name
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <UserIcon size={16} />
                </div>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Sarah Connor"
                  className="block w-full pl-10 pr-3 py-2.5 bg-white border border-slate-200 rounded-xl text-sm placeholder-slate-400 text-slate-900 focus:outline-none focus:border-red-500 focus:ring-4 focus:ring-red-500/10 transition-all"
                />
              </div>
            </div>

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
                  placeholder="sarah@enterprise.com"
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
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Min. 8 characters"
                  className="block w-full pl-10 pr-3 py-2.5 bg-white border border-slate-200 rounded-xl text-sm placeholder-slate-400 text-slate-900 focus:outline-none focus:border-red-500 focus:ring-4 focus:ring-red-500/10 transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Confirm Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock size={16} />
                </div>
                <input
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Repeat password"
                  className="block w-full pl-10 pr-3 py-2.5 bg-white border border-slate-200 rounded-xl text-sm placeholder-slate-400 text-slate-900 focus:outline-none focus:border-red-500 focus:ring-4 focus:ring-red-500/10 transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={registerMutation.isPending || isSuccess}
              className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-xl shadow-xs text-sm font-semibold text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-4 focus:ring-red-500/20 disabled:opacity-50 transition-colors cursor-pointer"
            >
              {registerMutation.isPending ? 'Registering...' : 'Create Account'}
            </button>
          </form>

          <div className="mt-6 border-t border-slate-100 pt-4 text-center">
            <p className="text-sm text-slate-500">
              Already have an account?{' '}
              <Link to="/login" className="font-semibold text-red-600 hover:text-red-700">
                Sign In
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
