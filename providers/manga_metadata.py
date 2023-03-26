from dataclasses import dataclass
from PIL import Image

@dataclass
class MangaMetadata():
    provider: str
    id_token: str
    titles: list[str]
    tags: list[str]
    genres: list[str]
    summary: str
    cover_art: Image.Image

    def __repr__(self) -> str:
        return str({
            "provider": self.provider,
            "id_token": self.id_token,
            "titles": self.titles,
            "tags": self.tags,
            "genres": self.genres,
            "summary": self.summary,
            "cover_art": self.cover_art
        })
