"""
Google Drive tools for CSman — organize files, create folders, export PDFs.
"""

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth import get_google_credentials
import io

_drive_service = None


def _get_drive_service():
    """Lazily builds the Drive API client."""
    global _drive_service
    if _drive_service is None:
        creds = get_google_credentials()
        _drive_service = build("drive", "v3", credentials=creds)
    return _drive_service


def create_folder(folder_name, parent_folder_id=None):
    """
    Creates a new folder in Google Drive.
    If parent_folder_id is provided, creates it inside that folder.
    """
    service = _get_drive_service()

    file_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }

    if parent_folder_id:
        file_metadata["parents"] = [parent_folder_id]

    folder = service.files().create(body=file_metadata, fields="id,webViewLink").execute()

    return {
        "status": "created",
        "folder_id": folder.get("id"),
        "folder_name": folder_name,
        "link": folder.get("webViewLink"),
    }


def list_files(folder_id=None, query=None, max_results=10):
    """
    Lists files in Google Drive.
    If folder_id provided, lists files in that folder.
    If query provided (e.g., "name contains 'lab'"), filters by that query.
    """
    service = _get_drive_service()

    q = None
    if folder_id:
        q = f"'{folder_id}' in parents and trashed=false"
    if query:
        q = (q + " and " if q else "") + query

    results = service.files().list(
        q=q,
        spaces="drive",
        fields="files(id, name, mimeType, webViewLink, createdTime)",
        pageSize=max_results,
    ).execute()

    files = results.get("files", [])
    return {
        "count": len(files),
        "files": [
            {
                "id": f["id"],
                "name": f["name"],
                "type": f["mimeType"],
                "link": f["webViewLink"],
                "created": f.get("createdTime"),
            }
            for f in files
        ],
    }


def export_doc_as_pdf(doc_id, pdf_name=None, folder_id=None):
    """
    Exports a Google Doc as a PDF and saves it to Drive.
    If folder_id provided, saves the PDF to that folder.
    Returns the PDF file ID and link.
    """
    service = _get_drive_service()

    # Export the Doc as PDF
    pdf_content = service.files().export(fileId=doc_id, mimeType="application/pdf").execute()

    # Create the PDF file in Drive
    pdf_metadata = {
        "name": pdf_name or "document.pdf",
        "mimeType": "application/pdf",
    }

    if folder_id:
        pdf_metadata["parents"] = [folder_id]

    pdf_file = service.files().create(
        body=pdf_metadata,
        media_body=io.BytesIO(pdf_content),
        fields="id,webViewLink",
    ).execute()

    return {
        "status": "exported",
        "pdf_id": pdf_file.get("id"),
        "pdf_name": pdf_name or "document.pdf",
        "link": pdf_file.get("webViewLink"),
    }


def organize_files_into_project_folder(project_name, doc_ids):
    """
    Creates a project folder and moves the given doc IDs into it.
    Useful for organizing study materials or project documentation.
    """
    service = _get_drive_service()

    # Create the project folder
    folder_metadata = {
        "name": project_name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    folder = service.files().create(body=folder_metadata, fields="id").execute()
    folder_id = folder.get("id")

    # Move each doc into the folder
    for doc_id in doc_ids:
        service.files().update(
            fileId=doc_id,
            addParents=folder_id,
            fields="id, parents",
        ).execute()

    return {
        "status": "organized",
        "folder_id": folder_id,
        "folder_name": project_name,
        "docs_moved": len(doc_ids),
    }


def delete_file(file_id):
    """
    Deletes a file or folder from Google Drive (moves to trash).
    """
    service = _get_drive_service()
    service.files().delete(fileId=file_id).execute()
    return {"status": "deleted", "file_id": file_id}


DRIVE_TOOL_DEFS = [
    {
        "name": "create_folder",
        "description": (
            "Create a new folder in Google Drive to organize project files, "
            "study materials, or labs. Optionally place it inside another folder."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "folder_name": {"type": "string", "description": "Name of the new folder"},
                "parent_folder_id": {"type": "string", "description": "Optional parent folder ID"},
            },
            "required": ["folder_name"],
        },
    },
    {
        "name": "list_files",
        "description": (
            "List files and folders in Google Drive. Search by folder or by query "
            "(e.g., 'name contains Lab')."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "folder_id": {"type": "string", "description": "Optional folder ID to list files in"},
                "query": {"type": "string", "description": "Optional search query (e.g., 'name contains REST')"},
                "max_results": {"type": "integer", "description": "Max files to return (default 10)"},
            },
            "required": [],
        },
    },
    {
        "name": "export_doc_as_pdf",
        "description": (
            "Export a Google Doc as a PDF and save it to Drive. Useful for "
            "creating downloadable study guides, reports, or project documentation."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "doc_id": {"type": "string", "description": "The Google Doc ID to export"},
                "pdf_name": {"type": "string", "description": "Optional PDF filename"},
                "folder_id": {"type": "string", "description": "Optional folder ID to save PDF in"},
            },
            "required": ["doc_id"],
        },
    },
    {
        "name": "organize_files_into_project_folder",
        "description": (
            "Create a project folder and move multiple docs into it. "
            "Great for organizing study materials or project deliverables."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Name of the project folder"},
                "doc_ids": {
                    "type": "array",
                    "description": "List of Google Doc IDs to move into the folder",
                    "items": {"type": "string"},
                },
            },
            "required": ["project_name", "doc_ids"],
        },
    },
    {
        "name": "delete_file",
        "description": "Delete a file or folder from Google Drive.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_id": {"type": "string", "description": "The file/folder ID to delete"},
            },
            "required": ["file_id"],
        },
    },
]


def call_drive_tool(name, tool_input):
    """Dispatches tool_use calls to Drive functions."""
    if name == "create_folder":
        return create_folder(**tool_input)
    if name == "list_files":
        return list_files(**tool_input)
    if name == "export_doc_as_pdf":
        return export_doc_as_pdf(**tool_input)
    if name == "organize_files_into_project_folder":
        return organize_files_into_project_folder(**tool_input)
    if name == "delete_file":
        return delete_file(**tool_input)
    return {"error": f"Unknown tool: {name}"}