"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { logout, isAuthenticated } from "@/lib/auth";

export default function UserDashboard() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (!isAuthenticated()) {
      router.push("/login");
    }
  }, [router]);

  if (!mounted || !isAuthenticated()) {
    return <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col">
      {/* Header */}
      <header className="border-b border-white/10 bg-slate-900/50 px-8 py-5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-indigo-600 flex items-center justify-center">
            <svg className="h-4 w-4 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
            </svg>
          </div>
          <h1 className="text-xl font-semibold text-white tracking-tight">User Dashboard</h1>
        </div>
        <button
          onClick={logout}
          className="rounded-lg bg-white/5 px-4 py-2 text-sm font-medium text-slate-300 hover:bg-white/10 hover:text-white transition-all"
        >
          Sign out
        </button>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-4xl w-full mx-auto p-8 mt-10">
        <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm p-10 text-center">
          <h2 className="text-2xl font-bold text-white mb-4">Welcome to your account!</h2>
          <p className="text-slate-400 mb-8 max-w-lg mx-auto">
            You have successfully logged in. This action fired the &quot;LOGIN&quot; trigger in the backend, which dispatches notifications based on the admin&apos;s settings.
          </p>
          <div className="inline-flex items-center gap-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 px-4 py-2 text-sm text-emerald-400">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            Active Session
          </div>
        </div>
      </main>
    </div>
  );
}
