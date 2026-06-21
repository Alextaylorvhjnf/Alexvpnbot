import json
from pathlib import Path
from datetime import datetime, timedelta, date
from typing import Dict, List, Any

class AdminPanel:
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.users_file = self.data_dir / "users.json"
        self.chats_file = self.data_dir / "chats.json"
        self.events_file = self.data_dir / "events.json"
        self._init_files()

    def _init_files(self):
        for f in [self.users_file, self.chats_file, self.events_file]:
            if not f.exists():
                f.write_text("[]", encoding="utf-8")

    def add_user(self, user_id: int, username: str, full_name: str):
        users = self._read(self.users_file)
        existing = next((u for u in users if u["user_id"] == user_id), None)
        if existing:
            existing["last_seen"] = datetime.now().isoformat()
            existing["username"] = username
            existing["full_name"] = full_name
            existing["message_count"] = existing.get("message_count", 0) + 1
        else:
            users.append({
                "user_id": user_id, "username": username, "full_name": full_name,
                "first_seen": datetime.now().isoformat(), "last_seen": datetime.now().isoformat(),
                "message_count": 1, "is_blocked": False
            })
        self._write(self.users_file, users)

    def log_chat(self, user_id: int, username: str, full_name: str, user_message: str, bot_response: str):
        chats = self._read(self.chats_file)
        chats.append({
            "user_id": user_id, "username": username, "full_name": full_name,
            "user_message": user_message[:1000], "bot_response": bot_response[:1000],
            "timestamp": datetime.now().isoformat()
        })
        if len(chats) > 5000: chats = chats[-5000:]
        self._write(self.chats_file, chats)

    def log_event(self, event_type: str, description: str, user_id: int = None):
        events = self._read(self.events_file)
        events.append({
            "event_type": event_type, "description": description,
            "user_id": user_id, "timestamp": datetime.now().isoformat()
        })
        if len(events) > 1000: events = events[-1000:]
        self._write(self.events_file, events)

    def get_stats(self) -> Dict[str, Any]:
        users = self._read(self.users_file)
        chats = self._read(self.chats_file)
        now = datetime.now()
        today = now.date()
        yesterday = today - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        return {
            "total_users": len(users),
            "today_users": len([u for u in users if self._date_eq(u.get("last_seen"), today)]),
            "yesterday_users": len([u for u in users if self._date_eq(u.get("last_seen"), yesterday)]),
            "week_users": len([u for u in users if self._after(u.get("last_seen"), week_ago)]),
            "month_users": len([u for u in users if self._after(u.get("last_seen"), month_ago)]),
            "active_24h": len([u for u in users if self._after(u.get("last_seen"), now - timedelta(hours=24))]),
            "total_chats": len(chats),
            "today_chats": len([c for c in chats if self._date_eq(c.get("timestamp"), today)]),
            "yesterday_chats": len([c for c in chats if self._date_eq(c.get("timestamp"), yesterday)]),
            "week_chats": len([c for c in chats if self._after(c.get("timestamp"), week_ago)]),
            "month_chats": len([c for c in chats if self._after(c.get("timestamp"), month_ago)]),
        }

    def get_users_by_period(self, period: str) -> List[Dict]:
        users = self._read(self.users_file)
        return self._filter(users, period, "last_seen")

    def get_chats_by_period(self, period: str, limit: int = 20) -> List[Dict]:
        chats = self._read(self.chats_file)
        filtered = self._filter(chats, period, "timestamp")
        filtered.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return filtered[:limit]

    def get_events_by_period(self, period: str = "week", limit: int = 20) -> List[Dict]:
        events = self._read(self.events_file)
        filtered = self._filter(events, period, "timestamp")
        filtered.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return filtered[:limit]

    def get_top_users(self, period: str = "week", limit: int = 10) -> List[Dict]:
        chats = self._read(self.chats_file)
        filtered = self._filter(chats, period, "timestamp")
        user_counts = {}
        for c in filtered:
            uid = c["user_id"]
            if uid not in user_counts:
                user_counts[uid] = {"user_id": uid, "username": c.get("username", ""), "full_name": c.get("full_name", ""), "count": 0}
            user_counts[uid]["count"] += 1
        return sorted(user_counts.values(), key=lambda x: x["count"], reverse=True)[:limit]

    def _filter(self, data, period, key):
        now = datetime.now()
        today = now.date()
        if period == "today": return [d for d in data if self._date_eq(d.get(key), today)]
        elif period == "yesterday": return [d for d in data if self._date_eq(d.get(key), today - timedelta(days=1))]
        elif period == "week": return [d for d in data if self._after(d.get(key), now - timedelta(days=7))]
        elif period == "month": return [d for d in data if self._after(d.get(key), now - timedelta(days=30))]
        elif period == "day": return [d for d in data if self._after(d.get(key), now - timedelta(hours=24))]
        else: return data

    def _date_eq(self, iso_str, d): 
        try: return datetime.fromisoformat(iso_str).date() == d
        except: return False
    def _after(self, iso_str, cutoff):
        try: return datetime.fromisoformat(iso_str) > cutoff
        except: return False
    def _read(self, path):
        try:
            c = path.read_text(encoding="utf-8")
            return json.loads(c) if c.strip() else []
        except: return []
    def _write(self, path, data):
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

admin = AdminPanel()
