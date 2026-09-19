interface BadgeProps {
  status: "configured" | "unconfigured" | "on" | "off";
}

const config = {
  configured: { label: "Configured", classes: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30" },
  unconfigured: { label: "Not configured", classes: "bg-slate-500/15 text-slate-400 border border-slate-500/30" },
  on: { label: "ON", classes: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30" },
  off: { label: "OFF", classes: "bg-rose-500/15 text-rose-400 border border-rose-500/30" },
};

export default function Badge({ status }: BadgeProps) {
  const { label, classes } = config[status];
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${classes}`}>
      <span className={`mr-1.5 h-1.5 w-1.5 rounded-full ${
        status === "on" || status === "configured" ? "bg-emerald-400" : 
        status === "off" ? "bg-rose-400" : "bg-slate-400"
      }`} />
      {label}
    </span>
  );
}
