import dateparser
from datetime import datetime
import pytz

def parse_date_phrase(phrase):
    return dateparser.parse(phrase, settings={
        "PREFER_DATES_FROM": "future",
        "TIMEZONE": "Europe/Berlin",
        "RETURN_AS_TIMEZONE_AWARE": True
    })
