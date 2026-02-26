import json
import uuid
from datetime import datetime

from app.config import NOTES_FILE as DATA_FILE, TAGS_FILE, CHATS_FILE, MAX_CHATS


def _ensure_file():
    """Create data dir and empty notes file if they don't exist."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps({'notes': []}, indent=2), encoding='utf-8')


def load_notes() -> list[dict]:
    """Return all notes as a list of dicts."""
    _ensure_file()
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('notes', [])


def save_note(title: str, content: str, source_type: str,
              source_name: str, source_author: str, tags: list[str]) -> dict:
    """Create a new note, persist it, and return the created note dict."""
    _ensure_file()
    notes = load_notes()
    note = {
        'id': str(uuid.uuid4()),
        'title': title.strip(),
        'content': content.strip(),
        'source_type': source_type,
        'source_name': source_name.strip(),
        'source_author': source_author.strip(),
        'tags': [t.strip().lower() for t in tags if t.strip()],
        'created_at': datetime.now().isoformat(timespec='seconds'),
    }
    notes.append(note)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({'notes': notes}, f, indent=2, ensure_ascii=False)
    try:
        from app.services import rag_service
        rag_service.add_note(note)
    except Exception:
        pass
    return note


def delete_note(note_id: str) -> bool:
    """Delete note by ID. Returns True if found and deleted."""
    notes = load_notes()
    original_len = len(notes)
    notes = [n for n in notes if n['id'] != note_id]
    if len(notes) < original_len:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({'notes': notes}, f, indent=2, ensure_ascii=False)
        try:
            from app.services import rag_service
            rag_service.delete_note(note_id)
        except Exception:
            pass
        return True
    return False


def update_note(note_id: str, title: str, content: str, source_type: str,
                source_name: str, source_author: str, tags: list[str]) -> bool:
    """Update an existing note by ID. Returns True if found and updated."""
    notes = load_notes()
    for note in notes:
        if note['id'] == note_id:
            note['title'] = title.strip()
            note['content'] = content.strip()
            note['source_type'] = source_type
            note['source_name'] = source_name.strip()
            note['source_author'] = source_author.strip()
            note['tags'] = [t.strip().lower() for t in tags if t.strip()]
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump({'notes': notes}, f, indent=2, ensure_ascii=False)
            try:
                from app.services import rag_service
                rag_service.update_note(note_id, note)
            except Exception:
                pass
            return True
    return False


# --- Tag operations ---

def _ensure_tags_file():
    """Create tags.json if it doesn't exist."""
    TAGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not TAGS_FILE.exists():
        TAGS_FILE.write_text(json.dumps({'tags': []}, indent=2), encoding='utf-8')


def load_tags() -> list[dict]:
    """Return all tags as a list of dicts with id and name."""
    _ensure_tags_file()
    with open(TAGS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('tags', [])


def save_tag(name: str) -> dict | None:
    """Create a new tag. Returns the tag dict, or None if it already exists."""
    _ensure_tags_file()
    tags = load_tags()
    normalized = name.strip().lower()
    if not normalized:
        return None
    if any(t['name'] == normalized for t in tags):
        return None
    tag = {
        'id': str(uuid.uuid4()),
        'name': normalized,
    }
    tags.append(tag)
    with open(TAGS_FILE, 'w', encoding='utf-8') as f:
        json.dump({'tags': tags}, f, indent=2, ensure_ascii=False)
    return tag


def delete_tag(tag_id: str) -> bool:
    """Delete tag by ID. Returns True if found and deleted."""
    tags = load_tags()
    original_len = len(tags)
    tags = [t for t in tags if t['id'] != tag_id]
    if len(tags) < original_len:
        with open(TAGS_FILE, 'w', encoding='utf-8') as f:
            json.dump({'tags': tags}, f, indent=2, ensure_ascii=False)
        return True
    return False


# --- Chat operations ---

def _ensure_chats_file():
    """Create chats.json if it doesn't exist."""
    CHATS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not CHATS_FILE.exists():
        CHATS_FILE.write_text(json.dumps({'chats': []}, indent=2), encoding='utf-8')


def load_chats() -> list[dict]:
    """Return all chats as a list of dicts, sorted by updated_at descending."""
    _ensure_chats_file()
    with open(CHATS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    chats = data.get('chats', [])
    return sorted(chats, key=lambda c: c.get('updated_at', ''), reverse=True)


def get_chat(chat_id: str) -> dict | None:
    """Return a single chat by ID, or None if not found."""
    _ensure_chats_file()
    with open(CHATS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for chat in data.get('chats', []):
        if chat['id'] == chat_id:
            return chat
    return None


def save_chat(title: str, messages: list[dict]) -> dict | None:
    """Create a new chat. Returns the chat dict, or None if limit reached."""
    _ensure_chats_file()
    with open(CHATS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    chats = data.get('chats', [])
    if len(chats) >= MAX_CHATS:
        return None
    now = datetime.now().isoformat(timespec='seconds')
    chat = {
        'id': str(uuid.uuid4()),
        'title': title[:50],
        'messages': messages,
        'created_at': now,
        'updated_at': now,
    }
    chats.append(chat)
    with open(CHATS_FILE, 'w', encoding='utf-8') as f:
        json.dump({'chats': chats}, f, indent=2, ensure_ascii=False)
    return chat


def update_chat(chat_id: str, messages: list[dict],
                title: str | None = None) -> bool:
    """Update a chat's messages and updated_at. Optionally update title.
    Returns True if found and updated."""
    _ensure_chats_file()
    with open(CHATS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    chats = data.get('chats', [])
    for chat in chats:
        if chat['id'] == chat_id:
            chat['messages'] = messages
            if title is not None:
                chat['title'] = title[:50]
            chat['updated_at'] = datetime.now().isoformat(timespec='seconds')
            with open(CHATS_FILE, 'w', encoding='utf-8') as f:
                json.dump({'chats': chats}, f, indent=2, ensure_ascii=False)
            return True
    return False


def delete_chat(chat_id: str) -> bool:
    """Delete chat by ID. Returns True if found and deleted."""
    _ensure_chats_file()
    with open(CHATS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    chats = data.get('chats', [])
    original_len = len(chats)
    chats = [c for c in chats if c['id'] != chat_id]
    if len(chats) < original_len:
        with open(CHATS_FILE, 'w', encoding='utf-8') as f:
            json.dump({'chats': chats}, f, indent=2, ensure_ascii=False)
        return True
    return False


def count_chats() -> int:
    """Return the number of saved chats."""
    return len(load_chats())
