"""
Google Docs tools for CSman — create and edit study guides, lab reports, notes.
"""

from googleapiclient.discovery import build
from google_auth import get_google_credentials

_docs_service = None
_drive_service = None


def _get_docs_service():
    """Lazily builds the Docs API client."""
    global _docs_service
    if _docs_service is None:
        creds = get_google_credentials()
        _docs_service = build("docs", "v1", credentials=creds)
    return _docs_service


def _get_drive_service():
    """Lazily builds the Drive API client."""
    global _drive_service
    if _drive_service is None:
        creds = get_google_credentials()
        _drive_service = build("drive", "v3", credentials=creds)
    return _drive_service


def create_doc(title, content_text="", folder_id=None):
    """
    Creates a new Google Doc with the given title and optional content.
    If folder_id is provided, the doc is placed in that folder.
    Returns the doc ID and link.
    """
    drive_service = _get_drive_service()
    docs_service = _get_docs_service()

    # Create the document
    doc_body = {"title": title}
    doc = docs_service.documents().create(body=doc_body).execute()
    doc_id = doc.get("documentId")

    # If folder_id provided, move the doc there
    if folder_id:
        drive_service.files().update(
            fileId=doc_id,
            addParents=folder_id,
            fields="id, parents"
        ).execute()

    # Add initial content if provided
    if content_text:
        requests = [
            {
                "insertText": {
                    "text": content_text,
                    "location": {"index": 1},
                }
            }
        ]
        docs_service.documents().batchUpdate(
            documentId=doc_id, body={"requests": requests}
        ).execute()

    # Get the doc link
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

    return {
        "status": "created",
        "doc_id": doc_id,
        "title": title,
        "link": doc_url,
    }


def append_to_doc(doc_id, content_text):
    """
    Appends text to an existing Google Doc.
    """
    docs_service = _get_docs_service()

    # Get document to find insertion point
    doc = docs_service.documents().get(documentId=doc_id).execute()
    end_index = doc["body"]["content"][-1]["endIndex"]

    requests = [
        {
            "insertText": {
                "text": "\n" + content_text,
                "location": {"index": end_index - 1},
            }
        }
    ]
    docs_service.documents().batchUpdate(
        documentId=doc_id, body={"requests": requests}
    ).execute()

    return {"status": "appended", "doc_id": doc_id}


def format_doc_as_study_guide(doc_id, title, topics):
    """
    Formats a doc as a study guide with sections for each topic.
    topics is a list of dicts like [{"name": "REST APIs", "notes": "..."}, ...]
    """
    docs_service = _get_docs_service()

    requests = [
        {
            "insertText": {
                "text": title + "\n",
                "location": {"index": 1},
            }
        },
        {
            "updateTextStyle": {
                "range": {"startIndex": 1, "endIndex": len(title) + 1},
                "textStyle": {"bold": True, "fontSize": {"magnitude": 18, "unit": "pt"}},
                "fields": "bold,fontSize",
            }
        },
    ]

    current_index = len(title) + 2

    for topic in topics:
        topic_name = topic.get("name", "Untitled")
        topic_notes = topic.get("notes", "")

        requests.append({
            "insertText": {
                "text": "\n" + topic_name + "\n",
                "location": {"index": current_index},
            }
        })

        requests.append({
            "updateTextStyle": {
                "range": {
                    "startIndex": current_index + 1,
                    "endIndex": current_index + len(topic_name) + 1,
                },
                "textStyle": {"bold": True, "fontSize": {"magnitude": 14, "unit": "pt"}},
                "fields": "bold,fontSize",
            }
        })

        current_index += len(topic_name) + 2

        if topic_notes:
            requests.append({
                "insertText": {
                    "text": topic_notes + "\n",
                    "location": {"index": current_index},
                }
            })
            current_index += len(topic_notes) + 1

    docs_service.documents().batchUpdate(
        documentId=doc_id, body={"requests": requests}
    ).execute()

    return {"status": "formatted", "doc_id": doc_id, "topics": len(topics)}


def read_doc(doc_id):
    """
    Reads the text content of a Google Doc.
    """
    docs_service = _get_docs_service()
    doc = docs_service.documents().get(documentId=doc_id).execute()

    content = ""
    if "body" in doc and "content" in doc["body"]:
        for element in doc["body"]["content"]:
            if "paragraph" in element:
                for run in element["paragraph"].get("elements", []):
                    if "textRun" in run:
                        content += run["textRun"]["content"]

    return {
        "doc_id": doc_id,
        "title": doc.get("title", "Untitled"),
        "content": content[:500],
    }


DOCS_TOOL_DEFS = [
    {
        "name": "create_doc",
        "description": (
            "Create a new Google Doc for study guides, lab reports, notes, "
            "project documentation, or any content. Optionally place it in a Drive folder."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Doc title"},
                "content_text": {"type": "string", "description": "Optional initial content to add"},
                "folder_id": {"type": "string", "description": "Optional Google Drive folder ID to place doc in"},
            },
            "required": ["title"],
        },
    },
    {
        "name": "append_to_doc",
        "description": "Append text to an existing Google Doc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "doc_id": {"type": "string", "description": "The Google Doc ID"},
                "content_text": {"type": "string", "description": "Text to append"},
            },
            "required": ["doc_id", "content_text"],
        },
    },
    {
        "name": "format_doc_as_study_guide",
        "description": (
            "Format a Google Doc as a study guide with sections for each topic. "
            "Pass a list of topics with names and notes."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "doc_id": {"type": "string", "description": "The Google Doc ID"},
                "title": {"type": "string", "description": "Study guide title"},
                "topics": {
                    "type": "array",
                    "description": "List of topics, each with 'name' and 'notes'",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "notes": {"type": "string"},
                        },
                        "required": ["name"],
                    },
                },
            },
            "required": ["doc_id", "title", "topics"],
        },
    },
    {
        "name": "read_doc",
        "description": "Read the text content of a Google Doc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "doc_id": {"type": "string", "description": "The Google Doc ID"},
            },
            "required": ["doc_id"],
        },
    },
]


def call_docs_tool(name, tool_input):
    """Dispatches tool_use calls to Docs functions."""
    if name == "create_doc":
        return create_doc(**tool_input)
    if name == "append_to_doc":
        return append_to_doc(**tool_input)
    if name == "format_doc_as_study_guide":
        return format_doc_as_study_guide(**tool_input)
    if name == "read_doc":
        return read_doc(**tool_input)
    return {"error": f"Unknown tool: {name}"}