import os
from datetime import datetime, timedelta, time as dt_time
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pytz
import json

SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_INFO = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
CALENDAR_ID = os.environ["CALENDAR_ID"]
TIMEZONE = "Europe/Berlin"

credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_INFO, scopes=SCOPES)
service = build("calendar", "v3", credentials=credentials)

def _get_events(date):
    start = datetime.combine(date, dt_time(8, 0)).isoformat() + "+02:00"
    end = datetime.combine(date, dt_time(18, 0)).isoformat() + "+02:00"
    events_result = service.events().list(calendarId=CALENDAR_ID, timeMin=start, timeMax=end).execute()
    return events_result.get("items", [])

def _build_datetime(date_str, time_str):
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    tz = pytz.timezone(TIMEZONE)
    dt = dt.replace(second=0, microsecond=0)
    return tz.localize(dt)

def check_availability(date, time):
    dt = _build_datetime(date, time)
    events = _get_events(dt.date())
    for event in events:
        if event["start"]["dateTime"][:16] == dt.isoformat()[:16]:
            return {"available": False}
    return {"available": True}

def get_available_slots(date_str):
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    events = _get_events(date)
    booked_times = [e["start"]["dateTime"][11:16] for e in events]
    available = []
    for hour in range(8, 18):
        t = f"{hour:02}:00"
        if t not in booked_times:
            available.append(t)
    return {"available_slots": available}

def get_next_free_slots():
    slots = []
    current = datetime.now(pytz.timezone(TIMEZONE)).date()
    while len(slots) < 3:
        if current.weekday() < 5:
            free = get_available_slots(current.isoformat())["available_slots"]
            for time in free:
                slots.append({"date": current.isoformat(), "time": time})
                if len(slots) == 3:
                    break
        current += timedelta(days=1)
    return {"next_slots": slots}

def book_slot(date, time, name):
    dt_start = _build_datetime(date, time)
    dt_end = dt_start + timedelta(hours=1)
    event = {
        "summary": f"Probetraining – {name}",
        "start": {"dateTime": dt_start.isoformat(), "timeZone": TIMEZONE},
        "end": {"dateTime": dt_end.isoformat(), "timeZone": TIMEZONE},
    }
    service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return {"status": "booked"}

def delete_slot(date, time):
    dt = _build_datetime(date, time)
    events = _get_events(dt.date())
    for event in events:
        if event["start"]["dateTime"][:16] == dt.isoformat()[:16]:
            service.events().delete(calendarId=CALENDAR_ID, eventId=event["id"]).execute()
            return {"status": "deleted"}
    return {"status": "not found"}

def reschedule_slot(old_date, old_time, new_date, new_time, name):
    delete_slot(old_date, old_time)
    return book_slot(new_date, new_time, name)
