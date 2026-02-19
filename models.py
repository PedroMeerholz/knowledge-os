from dataclasses import dataclass, field
from datetime import datetime

SOURCE_TYPES = ['livro', 'video', 'artigo', 'podcast', 'curso', 'outro']


@dataclass
class Note:
    id: str
    title: str
    content: str
    source_type: str
    source_name: str
    tags: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec='seconds'))
