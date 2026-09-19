import os
import logging
import requests
from dotenv import load_dotenv
from .base import SendResult

load_dotenv()
logger = logging.getLogger(__name__)

ONESIGNAL_NOTIFICATION_URL = "https://onesignal.com/api/v1/notifications"


class WebPushService:
    def __init__(self):
        self.app_id = os.getenv("ONESIGNAL_APP_ID")
        # REST API key is NEVER sent to the frontend — only used server-side here
        self.rest_api_key = os.getenv("ONESIGNAL_REST_API_KEY")

    def _headers(self):
        return {
            "Authorization": f"Basic {self.rest_api_key}",
            "Content-Type": "application/json",
        }

    def send_to_player(self, player_id, title, message):
        """
        Send a Web Push notification to a single OneSignal player/subscription.
        Returns True on success, False on failure.
        """
        if not self.app_id or not self.rest_api_key:
            logger.error("Cannot send Web Push: ONESIGNAL_APP_ID or ONESIGNAL_REST_API_KEY missing.")
            return SendResult(
                success=False,
                response={"provider": "onesignal", "reason": "missing_credentials"},
                error_message="ONESIGNAL_APP_ID or ONESIGNAL_REST_API_KEY missing.",
            )

        payload = {
            "app_id": self.app_id,
            "include_player_ids": [player_id],
            "headings": {"en": title},
            "contents": {"en": message},
            # Restrict to Web Push only — no mobile
            "isAnyWeb": True,
            "isIos": False,
            "isAndroid": False,
        }

        try:
            response = requests.post(ONESIGNAL_NOTIFICATION_URL, json=payload, headers=self._headers(), timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Web Push sent to player {player_id}. Notification ID: {data.get('id')}")
            return SendResult(
                success=True,
                response={
                    "provider": "onesignal",
                    "player_id": player_id,
                    "status_code": response.status_code,
                    "body": data,
                },
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Web Push to player {player_id}. Error: {str(e)}")
            response_data = {
                "provider": "onesignal",
                "player_id": player_id,
                "error": str(e),
            }
            if e.response is not None:
                logger.error(f"OneSignal Response: {e.response.text}")
                response_data["status_code"] = e.response.status_code
                try:
                    response_data["body"] = e.response.json()
                except ValueError:
                    response_data["body"] = e.response.text
            return SendResult(
                success=False,
                response=response_data,
                error_message=str(e),
            )

    def send_to_user_players(self, player_ids, title, message):
        """
        Send Web Push to a list of player_ids (a user may have multiple browser subscriptions).
        Continues even if individual sends fail.
        """
        results = []
        for player_id in player_ids:
            results.append(self.send_to_player(player_id, title, message))
        return SendResult(
            success=all(result.success for result in results),
            response={
                "provider": "onesignal",
                "results": [
                    {
                        "success": result.success,
                        "response": result.response,
                        "error_message": result.error_message,
                    }
                    for result in results
                ],
            },
            error_message="; ".join(result.error_message for result in results if result.error_message),
        )
