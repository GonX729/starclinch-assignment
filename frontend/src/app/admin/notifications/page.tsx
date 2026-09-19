"use client";
import { useCallback, useEffect, useState } from "react";
import { Trigger, NotificationTemplate, Channel } from "@/lib/types";
import ChannelCell from "@/components/notifications/ChannelCell";
import api from "@/lib/api";

const CHANNELS: { key: Channel; label: string }[] = [
  { key: "WHATSAPP", label: "WhatsApp" },
  { key: "EMAIL", label: "Email" },
  { key: "WEB_PUSH", label: "Web Push" },
];

export default function NotificationsPage() {
  const [triggers, setTriggers] = useState<Trigger[]>([]);
  const [templates, setTemplates] = useState<NotificationTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchData = useCallback(async () => {
    try {
      const [tRes, tmRes] = await Promise.all([
        api.get("/admin/triggers/"),
        api.get("/admin/templates/"),
      ]);
      setTriggers(tRes.data.results ?? tRes.data);
      setTemplates(tmRes.data.results ?? tmRes.data);
      setError("");
    } catch {
      setError("Failed to load data. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  /** Find the template for a given trigger + channel combination */
  function findTemplate(triggerId: string, channel: Channel) {
    return templates.find(
      (t) => t.trigger === triggerId && t.channel === channel
    );
  }

  return (
    <div className="px-8 py-8 max-w-6xl">
      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-xl font-semibold text-white">Notification Settings</h1>
        <p className="mt-1 text-sm text-slate-400">
          Configure templates for each trigger and channel. Enable or disable individual channels independently.
        </p>
      </div>

      {/* Error banner */}
      {error && (
        <div className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-sm text-red-400">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="overflow-hidden rounded-2xl border border-white/10 bg-slate-900">
        {loading ? (
          <div className="flex items-center justify-center py-24">
            <div className="flex flex-col items-center gap-3 text-slate-500">
              <span className="h-8 w-8 rounded-full border-2 border-slate-600 border-t-indigo-500 animate-spin" />
              <span className="text-sm">Loading…</span>
            </div>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10 bg-white/[0.02]">
                <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-slate-500 w-36">
                  Trigger
                </th>
                {CHANNELS.map((ch) => (
                  <th key={ch.key} className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                    {ch.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.05]">
              {triggers.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-16 text-center text-slate-500">
                    No triggers found. Seed the database with LOGIN and LOGOUT triggers.
                  </td>
                </tr>
              ) : (
                triggers.map((trigger) => (
                  <tr key={trigger.id} className="group hover:bg-white/[0.02] transition-colors">
                    {/* Trigger name */}
                    <td className="px-6 py-5">
                      <div className="flex flex-col gap-1">
                        <span className="font-medium text-white">{trigger.name}</span>
                        <code className="text-xs text-slate-500 font-mono">{trigger.event_key}</code>
                        <span className={`inline-flex items-center mt-0.5 text-xs ${trigger.active ? "text-emerald-400" : "text-slate-500"}`}>
                          <span className={`mr-1.5 h-1.5 w-1.5 rounded-full ${trigger.active ? "bg-emerald-400" : "bg-slate-600"}`} />
                          {trigger.active ? "Active" : "Inactive"}
                        </span>
                      </div>
                    </td>

                    {/* Channel cells */}
                    {CHANNELS.map((ch) => (
                      <td key={ch.key} className="px-6 py-5">
                        <ChannelCell
                          trigger={trigger}
                          channel={ch.key}
                          template={findTemplate(trigger.id, ch.key)}
                          onRefresh={fetchData}
                        />
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>

      {/* Legend */}
      <p className="mt-4 text-xs text-slate-600">
        Templates use <code className="text-indigo-400/70">{"{{name}}"}</code>, <code className="text-indigo-400/70">{"{{email}}"}</code>, <code className="text-indigo-400/70">{"{{phone}}"}</code> as dynamic variables.
      </p>
    </div>
  );
}
