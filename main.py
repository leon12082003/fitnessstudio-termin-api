from fastapi import FastAPI, Request
from calendar_utils import (
    check_availability, get_available_slots,
    get_next_free_slots, book_slot,
    delete_slot, reschedule_slot
)
from date_utils import parse_date_phrase

app = FastAPI()

@app.post("/check_availability")
async def api_check_availability(data: dict):
    return check_availability(data["date"], data["time"])

@app.post("/get_available_slots")
async def api_get_available_slots(data: dict):
    return get_available_slots(data["date"])

@app.post("/get_next_free_slots")
async def api_get_next_free_slots():
    return get_next_free_slots()

@app.post("/book_slot")
async def api_book_slot(data: dict):
    return book_slot(data["date"], data["time"], data["name"])

@app.post("/delete_slot")
async def api_delete_slot(data: dict):
    return delete_slot(data["date"], data["time"])

@app.post("/reschedule_slot")
async def api_reschedule_slot(data: dict):
    return reschedule_slot(data["old_date"], data["old_time"], data["new_date"], data["new_time"], data["name"])

@app.post("/handle_termin")
async def handle_termin(request: Request):
    data = await request.json()
    action = data.get("action")
    phrase = data.get("phrase")
    parsed_date = parse_date_phrase(phrase)
    return {"parsed_date": parsed_date.date().isoformat()}

