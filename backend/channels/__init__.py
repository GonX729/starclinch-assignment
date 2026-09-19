from .whatsapp import WhatsAppChannel
from .email_channel import EmailChannel
from .webpush_channel import WebPushChannel

CHANNEL_MAP = {
    'WHATSAPP': WhatsAppChannel(),
    'EMAIL': EmailChannel(),
    'WEB_PUSH': WebPushChannel(),
}

def get_channel(channel_code):
    return CHANNEL_MAP.get(channel_code)
