from fastapi import FastAPI, Request
from calendar_utils import (
    check_availability, get_available_slots,
    get_next_free_slots, book_slot,
    delete_slot, reschedule_slot
)
from date_utils import parse_date_phrase

app = FastAPI()

def normalize_phrase(phrase):
    # Alle Umwandlungen
    replacements = {
        "am ": "",  # z. B. „am 15. Juli“
    }

    # Wochentage vollständig
    weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    phrase_original = phrase  # für späteres .replace()

    phrase_lower = phrase.lower()
    for tag in weekdays:
        lower_tag = tag.lower()
        if f"{lower_tag} in einer woche" in phrase_lower:
            phrase = phrase.replace(f"{tag} in einer Woche", f"nächster {tag}")
        if f"diesen {lower_tag}" in phrase_lower:
            phrase = phrase.replace(f"diesen {tag}", f"kommender {tag}")
        if f"nächsten {lower_tag}" in phrase_lower:
            phrase = phrase.replace(f"nächsten {tag}", f"kommender {tag}")
        if f"kommenden {lower_tag}" in phrase_lower:
            phrase = phrase.replace(f"kommenden {tag}", f"kommender {tag}")

    for key, val in replacements.items():
        phrase = phrase.replace(key, val)

    return phrase

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
    phrase = normalize_phrase(data.get("phrase"))
    parsed_date = parse_date_phrase(phrase)
    if parsed_date:
        return {"parsed_date": parsed_date.date().isoformat()}
    else:
        return {"error": "Ungültige Formulierung oder nicht erkannt"}
