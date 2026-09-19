"use client";
import { useState } from "react";
import { NotificationTemplate, Trigger, Channel } from "@/lib/types";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import TemplateModal from "./TemplateModal";

interface ChannelCellProps {
  trigger: Trigger;
  channel: Channel;
  template?: NotificationTemplate;
  onRefresh: () => void;
}

const CHANNEL_ICONS: Record<Channel, string> = {
  WHATSAPP: "💬",
  EMAIL: "✉️",
  WEB_PUSH: "🔔",
};

export default function ChannelCell({
  trigger,
  channel,
  template,
  onRefresh,
}: ChannelCellProps) {
  const [modalOpen, setModalOpen] = useState(false);
  const configured = !!template;

  function handleSaved() {
    onRefresh();
  }

  return (
    <>
      <div className="flex flex-col gap-3">
        {/* Status row */}
        <div className="flex flex-wrap items-center gap-1.5">
          <Badge status={configured ? "configured" : "unconfigured"} />
          {configured && (
            <Badge status={template!.enabled ? "on" : "off"} />
          )}
        </div>

        {/* Action button */}
        <Button
          variant={configured ? "ghost" : "primary"}
          onClick={() => setModalOpen(true)}
          className="w-fit"
        >
          {configured ? (
            <>
              <span>{CHANNEL_ICONS[channel]}</span>
              Edit
            </>
          ) : (
            <>
              <span>＋</span>
              Configure
            </>
          )}
        </Button>
      </div>

      <TemplateModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSaved={handleSaved}
        triggerId={trigger.id}
        triggerName={trigger.name}
        channel={channel}
        existing={template}
      />
    </>
  );
}
