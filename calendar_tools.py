"""
Google Calendar tools for CSman.
"""

from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google_auth import get_google_credentials

_service = None


def _get_service():
    """Lazily builds (and caches) the Calendar API client."""
    global _service
    if _service is None:
        creds = get_google_credentials()
        _service = build("calendar", "v3", credentials=creds)
    return _service


def create_calendar_event(summary, start_time, end_time, description="", location=""):
    """
    Creates an event on the student's primary calendar.
    start_time / end_time must be ISO 8601, e.g. '2026-07-22T18:00:00'
    """
    service = _get_service()
    event = {
        "summary": summary,
        "description": description,
        "location": location,
        "start": {"dateTime": start_time, "timeZone": "Asia/Jerusalem"},
        "end": {"dateTime": end_time, "timeZone": "Asia/Jerusalem"},
    }
    created = service.events().insert(calendarId="primary", body=event).execute()
    return {
        "status": "created",
        "event_id": created.get("id"),
        "link": created.get("htmlLink"),
        "summary": summary,
        "start": start_time,
        "end": end_time,
    }


def list_upcoming_events(days_ahead=7, max_results=25):
    """Lists events on the primary calendar for the next N days."""
    service = _get_service()
    now = datetime.utcnow().isoformat() + "Z"
    later = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + "Z"

    result = service.events().list(
        calendarId="primary",
        timeMin=now,
        timeMax=later,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = result.get("items", [])
    return [
        {
            "id": e.get("id"),
            "summary": e.get("summary", "(no title)"),
            "start": e["start"].get("dateTime", e["start"].get("date")),
            "end": e["end"].get("dateTime", e["end"].get("date")),
        }
        for e in events
    ]


def update_calendar_event(event_id, summary=None, start_time=None, end_time=None):
    """Updates an existing event. Only pass the fields you want changed."""
    service = _get_service()
    event = service.events().get(calendarId="primary", eventId=event_id).execute()

    if summary:
        event["summary"] = summary
    if start_time:
        event["start"]["dateTime"] = start_time
    if end_time:
        event["end"]["dateTime"] = end_time

    updated = service.events().update(
        calendarId="primary", eventId=event_id, body=event
    ).execute()
    return {"status": "updated", "event_id": updated.get("id"), "summary": updated.get("summary")}


def delete_calendar_event(event_id):
    """Deletes an event from the primary calendar."""
    service = _get_service()
    service.events().delete(calendarId="primary", eventId=event_id).execute()
    return {"status": "deleted", "event_id": event_id}


CALENDAR_TOOL_DEFS = [
    {
        "name": "create_calendar_event",
        "description": (
            "Create a new event on the student's Google Calendar. Use this to "
            "schedule study sessions, lab work blocks, project deadlines, etc. "
            "Always use ISO 8601 datetimes (e.g. '2026-07-22T18:00:00')."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "Event title"},
                "start_time": {"type": "string", "description": "ISO 8601 start datetime"},
                "end_time": {"type": "string", "description": "ISO 8601 end datetime"},
                "description": {"type": "string", "description": "Optional event notes"},
                "location": {"type": "string", "description": "Optional location"},
            },
            "required": ["summary", "start_time", "end_time"],
        },
    },
    {
        "name": "list_upcoming_events",
        "description": (
            "List the student's upcoming Google Calendar events, so you know "
            "what's already scheduled before adding new study/lab blocks "
            "(avoid double-booking)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "days_ahead": {"type": "integer", "description": "How many days ahead to look (default 7)"},
                "max_results": {"type": "integer", "description": "Max events to return (default 25)"},
            },
            "required": [],
        },
    },
    {
        "name": "update_calendar_event",
        "description": "Update an existing calendar event's title or time.",
        "input_schema": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "The event ID to update"},
                "summary": {"type": "string", "description": "New title (optional)"},
                "start_time": {"type": "string", "description": "New ISO 8601 start time (optional)"},
                "end_time": {"type": "string", "description": "New ISO 8601 end time (optional)"},
            },
            "required": ["event_id"],
        },
    },
    {
        "name": "delete_calendar_event",
        "description": "Delete a calendar event by its event ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "The event ID to delete"},
            },
            "required": ["event_id"],
        },
    },
]


def call_calendar_tool(name, tool_input):
    """Dispatches a tool_use call from Claude to the matching function above."""
    if name == "create_calendar_event":
        return create_calendar_event(**tool_input)
    if name == "list_upcoming_events":
        return list_upcoming_events(**tool_input)
    if name == "update_calendar_event":
        return update_calendar_event(**tool_input)
    if name == "delete_calendar_event":
        return delete_calendar_event(**tool_input)
    return {"error": f"Unknown tool: {name}"}