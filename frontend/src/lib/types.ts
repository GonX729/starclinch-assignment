export interface Trigger {
  id: string;
  name: string;
  event_key: string;
  description: string;
  active: boolean;
}

export interface NotificationTemplate {
  id: string;
  trigger: string;
  trigger_detail: Trigger;
  channel: "WHATSAPP" | "EMAIL" | "WEB_PUSH";
  subject: string;
  body: string;
  enabled: boolean;
  variable_mappings: Record<string, string>;
  created_at: string;
  updated_at: string;
}

export type Channel = "WHATSAPP" | "EMAIL" | "WEB_PUSH";
