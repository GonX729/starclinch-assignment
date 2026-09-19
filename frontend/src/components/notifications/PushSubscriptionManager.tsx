"use client";
import { useEffect, useState } from "react";
import OneSignal from "react-onesignal";
import api from "@/lib/api";

export default function PushSubscriptionManager() {
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [loading, setLoading] = useState(false);
  const appId = process.env.NEXT_PUBLIC_ONESIGNAL_APP_ID;

  useEffect(() => {
    if (!appId) return;
    
    // Initialize OneSignal
    const initOneSignal = async () => {
      try {
        await OneSignal.init({
          appId: appId,
          allowLocalhostAsSecureOrigin: true
        });
      } catch {
        // OneSignal might throw if already initialized, ignore
      }
      
      const currentSub = OneSignal.User.PushSubscription.id;
      setIsSubscribed(!!currentSub && !!OneSignal.User.PushSubscription.optedIn);
    };

    initOneSignal();
  }, [appId]);

  const handleSubscribe = async () => {
    setLoading(true);
    try {
      await OneSignal.Slidedown.promptPush();
      const playerId = OneSignal.User.PushSubscription.id;
      if (playerId) {
        // Send to backend
        await api.post('/push/subscribe/', { player_id: playerId });
        setIsSubscribed(true);
      }
    } catch (err) {
      console.error("Push subscription failed", err);
    } finally {
      setLoading(false);
    }
  };

  const handleUnsubscribe = async () => {
    setLoading(true);
    try {
      const playerId = OneSignal.User.PushSubscription.id;
      if (playerId) {
        await api.delete('/push/subscribe/', { data: { player_id: playerId } });
      }
      await OneSignal.User.PushSubscription.optOut();
      setIsSubscribed(false);
    } catch (err) {
      console.error("Push unsubscription failed", err);
    } finally {
      setLoading(false);
    }
  };

  if (!appId) return null;

  return (
    <div className="flex flex-col gap-2 p-4 bg-slate-900 rounded-lg border border-white/10 mt-4">
      <h3 className="text-sm font-semibold text-white">Browser Push Notifications</h3>
      <p className="text-xs text-slate-400">
        {isSubscribed ? "You are subscribed to push notifications on this browser." : "Subscribe to receive push alerts for this browser."}
      </p>
      <button
        onClick={isSubscribed ? handleUnsubscribe : handleSubscribe}
        disabled={loading}
        className={`px-4 py-2 mt-2 rounded text-sm font-medium transition-all w-full ${
          isSubscribed 
            ? "bg-rose-500/10 text-rose-400 hover:bg-rose-500/20" 
            : "bg-indigo-600 text-white hover:bg-indigo-500"
        } disabled:opacity-50`}
      >
        {loading ? "Processing..." : (isSubscribed ? "Unsubscribe from Push" : "Enable Push Notifications")}
      </button>
    </div>
  );
}
