"use client";

import { useEffect, useState } from "react";
import { Channel, NotificationTemplate } from "@/lib/types";
import Modal from "@/components/ui/Modal";
import Button from "@/components/ui/Button";
import api from "@/lib/api";

interface TemplateModalProps {
  open: boolean;
  onClose: () => void;
  onSaved: () => void;
  triggerId: string;
  triggerName: string;
  channel: Channel;
  existing?: NotificationTemplate | null;
}

const CHANNEL_CONFIG: Record<
  Channel,
  {
    label: string;
    hasSubject: boolean;
    subjectLabel: string;
    subjectPlaceholder: string;
    bodyPlaceholder: string;
  }
> = {
  EMAIL: {
    label: "Email",
    hasSubject: true,
    subjectLabel: "Subject",
    subjectPlaceholder: "e.g. You just logged in to your account",
    bodyPlaceholder:
      "Hi {{name}},\n\nYou have successfully logged in.\n\nIf this was not you, contact support.",
  },
  WHATSAPP: {
    label: "WhatsApp",
    hasSubject: false,
    subjectLabel: "",
    subjectPlaceholder: "",
    bodyPlaceholder: "Hello {{name}}, welcome back!",
  },
  WEB_PUSH: {
    label: "Web Push",
    hasSubject: true,
    subjectLabel: "Title",
    subjectPlaceholder: "e.g. New login detected",
    bodyPlaceholder: "Welcome back, {{name}}!",
  },
};

const VARIABLES = [
  { key: "{{name}}", desc: "Full name or username" },
  { key: "{{email}}", desc: "Email address" },
  { key: "{{phone}}", desc: "Phone number" },
  { key: "{{username}}", desc: "Username" },
];

export default function TemplateModal({
  open,
  onClose,
  onSaved,
  triggerId,
  triggerName,
  channel,
  existing,
}: TemplateModalProps) {
  const cfg = CHANNEL_CONFIG[channel];
  const [template, setTemplate] = useState<NotificationTemplate | null>(existing ?? null);
  const isEditing = !!template;

  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [enabled, setEnabled] = useState(true);
  const [loadingTemplate, setLoadingTemplate] = useState(false);
  const [saving, setSaving] = useState(false);
  const [toggling, setToggling] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testFeedback, setTestFeedback] = useState<{ ok: boolean; msg: string } | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!open) return;

    setErrors({});
    setTestFeedback(null);

    if (!existing?.id) {
      setTemplate(null);
      setSubject("");
      setBody("");
      setEnabled(true);
      return;
    }

    setLoadingTemplate(true);
    api
      .get(`/admin/templates/${existing.id}/`)
      .then((res) => {
        const freshTemplate = res.data as NotificationTemplate;
        setTemplate(freshTemplate);
        setSubject(freshTemplate.subject ?? "");
        setBody(freshTemplate.body ?? "");
        setEnabled(freshTemplate.enabled);
      })
      .catch(() => {
        setTemplate(existing);
        setSubject(existing.subject ?? "");
        setBody(existing.body ?? "");
        setEnabled(existing.enabled);
        setErrors({ form: "Could not load the latest template details." });
      })
      .finally(() => setLoadingTemplate(false));
  }, [open, existing]);

  function validate() {
    const errs: Record<string, string> = {};
    if (cfg.hasSubject && !subject.trim()) {
      errs.subject = `${cfg.subjectLabel} is required.`;
    }
    if (!body.trim()) {
      errs.body = "Message body is required.";
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  }

  async function handleSave() {
    if (!validate()) return;
    setSaving(true);
    try {
      const payload = { subject, body, enabled };
      if (template) {
        await api.patch(`/admin/templates/${template.id}/`, payload);
      } else {
        await api.post("/admin/templates/", {
          trigger: triggerId,
          channel,
          ...payload,
        });
      }
      onSaved();
      onClose();
    } catch (e: unknown) {
      const data = (e as { response?: { data?: unknown } })?.response?.data;
      setErrors({
        form:
          typeof data === "string"
            ? data
            : JSON.stringify(data) || "Failed to save. Please try again.",
      });
    } finally {
      setSaving(false);
    }
  }

  async function handleToggle() {
    if (!template) return;
    setToggling(true);
    setErrors({});
    try {
      const res = await api.patch(`/admin/templates/${template.id}/toggle/`);
      const nextEnabled = Boolean(res.data.enabled);
      setEnabled(nextEnabled);
      setTemplate({ ...template, enabled: nextEnabled });
      onSaved();
    } catch {
      setErrors({ form: "Failed to toggle this channel. Please try again." });
    } finally {
      setToggling(false);
    }
  }

  async function handleTestSend() {
    if (!template) return;
    setTesting(true);
    setTestFeedback(null);
    try {
      const res = await api.post(`/admin/templates/${template.id}/test-send/`);
      setTestFeedback({ ok: true, msg: res.data.message || "Test sent." });
      onSaved();
      onClose();
    } catch (e: unknown) {
      const msg =
        (e as { response?: { data?: { message?: string } } })?.response?.data?.message ||
        "Test failed. Check admin contact details, browser subscription, API keys, and server logs.";
      setTestFeedback({ ok: false, msg });
    } finally {
      setTesting(false);
    }
  }

  function insertVariable(variable: string) {
    setBody((prev) => prev + variable);
  }

  return (
    <Modal
      open={open}
      title={`${isEditing ? "Edit" : "Configure"} Template - ${triggerName} / ${cfg.label}`}
      onClose={onClose}
      footer={
        <div className="flex w-full items-center justify-between gap-3">
          <div className="flex-1">
            {isEditing && (
              <Button
                variant="ghost"
                onClick={handleTestSend}
                loading={testing}
                disabled={saving || toggling || loadingTemplate}
              >
                Send test
              </Button>
            )}
          </div>
          <div className="flex gap-2">
            <Button variant="ghost" onClick={onClose} disabled={saving || testing || toggling}>
              Cancel
            </Button>
            <Button onClick={handleSave} loading={saving} disabled={testing || toggling || loadingTemplate}>
              {isEditing ? "Save changes" : "Create template"}
            </Button>
          </div>
        </div>
      }
    >
      <div className="space-y-5">
        {errors.form && (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-2.5 text-sm text-red-400">
            {errors.form}
          </div>
        )}

        {testFeedback && (
          <div
            className={`rounded-lg border px-4 py-2.5 text-sm ${
              testFeedback.ok
                ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
                : "border-red-500/30 bg-red-500/10 text-red-400"
            }`}
          >
            {testFeedback.msg}
          </div>
        )}

        {loadingTemplate ? (
          <div className="rounded-lg border border-white/10 bg-white/[0.03] px-4 py-8 text-center text-sm text-slate-400">
            Loading template...
          </div>
        ) : (
          <>
            {isEditing && (
              <div className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3">
                <div>
                  <p className="text-sm font-medium text-white">Channel status</p>
                  <p className="mt-0.5 text-xs text-slate-500">
                    Disabled templates will not send during real trigger events.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleToggle}
                  disabled={toggling || saving || testing}
                  className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none disabled:opacity-60 ${
                    enabled ? "bg-indigo-600" : "bg-slate-700"
                  }`}
                  aria-pressed={enabled}
                >
                  <span
                    className={`inline-block h-5 w-5 transform rounded-full bg-white shadow transition duration-200 ${
                      enabled ? "translate-x-5" : "translate-x-0"
                    }`}
                  />
                </button>
              </div>
            )}

            {cfg.hasSubject && (
              <div>
                <label className="mb-1.5 block text-xs font-medium text-slate-400">
                  {cfg.subjectLabel}
                </label>
                <input
                  value={subject}
                  onChange={(e) => {
                    setSubject(e.target.value);
                    if (errors.subject) setErrors((p) => ({ ...p, subject: "" }));
                  }}
                  placeholder={cfg.subjectPlaceholder}
                  className={`w-full rounded-lg border bg-white/5 px-3 py-2.5 text-sm text-white placeholder-slate-600 outline-none transition focus:ring-1 focus:ring-indigo-500/30 ${
                    errors.subject
                      ? "border-red-500/60 focus:border-red-500"
                      : "border-white/10 focus:border-indigo-500"
                  }`}
                />
                {errors.subject && <p className="mt-1 text-xs text-red-400">{errors.subject}</p>}
              </div>
            )}

            <div>
              <label className="mb-1.5 block text-xs font-medium text-slate-400">
                Message body
              </label>
              <textarea
                value={body}
                onChange={(e) => {
                  setBody(e.target.value);
                  if (errors.body) setErrors((p) => ({ ...p, body: "" }));
                }}
                rows={channel === "EMAIL" ? 6 : 4}
                placeholder={cfg.bodyPlaceholder}
                className={`w-full resize-none rounded-lg border bg-white/5 px-3 py-2.5 font-mono text-sm text-white placeholder-slate-600 outline-none transition focus:ring-1 focus:ring-indigo-500/30 ${
                  errors.body
                    ? "border-red-500/60 focus:border-red-500"
                    : "border-white/10 focus:border-indigo-500"
                }`}
              />
              {errors.body && <p className="mt-1 text-xs text-red-400">{errors.body}</p>}
            </div>

            <div>
              <p className="mb-2 text-xs font-medium text-slate-500">Click to insert variable</p>
              <div className="flex flex-wrap gap-2">
                {VARIABLES.map((v) => (
                  <button
                    key={v.key}
                    type="button"
                    onClick={() => insertVariable(v.key)}
                    title={v.desc}
                    className="group flex items-center gap-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-xs font-mono text-indigo-300 transition-all hover:border-indigo-400/50 hover:bg-indigo-500/20"
                  >
                    <span>{v.key}</span>
                    <span className="text-[10px] text-indigo-500 transition-colors group-hover:text-indigo-300">
                      - {v.desc}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </Modal>
  );
}
