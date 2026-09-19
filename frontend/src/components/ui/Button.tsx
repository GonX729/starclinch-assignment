import { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "ghost" | "danger" | "success";
  size?: "sm" | "md";
  loading?: boolean;
}

const variants = {
  primary: "bg-indigo-600 hover:bg-indigo-500 text-white shadow-sm",
  ghost: "bg-white/5 hover:bg-white/10 text-slate-300 border border-white/10",
  danger: "bg-red-600/20 hover:bg-red-600/30 text-red-400 border border-red-500/30",
  success: "bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30",
};

const sizes = {
  sm: "px-3 py-1.5 text-xs",
  md: "px-4 py-2 text-sm",
};

export default function Button({
  variant = "primary",
  size = "sm",
  loading = false,
  className = "",
  children,
  disabled,
  ...props
}: ButtonProps) {
  return (
    <button
      {...props}
      disabled={disabled || loading}
      className={`
        inline-flex items-center gap-1.5 rounded-lg font-medium
        transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed
        ${variants[variant]} ${sizes[size]} ${className}
      `}
    >
      {loading && (
        <span className="h-3 w-3 rounded-full border-2 border-current border-t-transparent animate-spin" />
      )}
      {children}
    </button>
  );
}
