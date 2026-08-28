"""Weekly report schedule is a valid future Asia/Jakarta Monday 07:00, and no schedule_key produced more than one scheduled (cron) run."""
import sys
from collections import Counter
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, "/app/backend")
from lib.reports import next_report_time  # noqa: E402  (pure helper, no app/DB import)

ADMIN_EMAIL = "admin@terataiputih2.sch.id"
ADMIN_PASSWORD = "TerataiAdmin2026!"


def test_next_report_time_is_future_monday_seven_am_jakarta():
    candidate = next_report_time()
    assert candidate.tzinfo is not None
    assert candidate.weekday() == 0  # Monday
    assert (candidate.hour, candidate.minute, candidate.second) == (7, 0, 0)
    now_jakarta = datetime.now(ZoneInfo("Asia/Jakarta"))
    assert candidate > now_jakarta


def test_scheduled_runs_never_share_a_schedule_key(client):
    login = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert login.status_code == 200, login.text

    overview = client.get("/admin/reports")
    assert overview.status_code == 200, overview.text
    runs = overview.json()["runs"]

    scheduled_keys = [r["schedule_key"] for r in runs if r["trigger"] == "scheduled"]
    counts = Counter(scheduled_keys)
    duplicated = [key for key, count in counts.items() if count > 1]
    assert duplicated == [], f"schedule_key(s) produced more than one scheduled run: {duplicated}"
