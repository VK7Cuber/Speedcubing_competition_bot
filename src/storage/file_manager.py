from pathlib import Path
from typing import Optional

BASE_DIR = Path("src/storage/scrambles")


def save_scramble_photo(base_path: Path, content: bytes) -> Path:
	base_path.parent.mkdir(parents=True, exist_ok=True)
	base_path.write_bytes(content)
	return base_path


def scramble_path(competition_id: int, discipline_id: int, attempt_number: int) -> Path:
	return BASE_DIR / f"competition_{competition_id}" / f"discipline_{discipline_id}" / f"attempt_{attempt_number}.jpg"


def get_scramble_photo_path(competition_id: int, discipline_id: int, attempt_number: int) -> Path:
	return scramble_path(competition_id, discipline_id, attempt_number)


def delete_competition_scrambles(competition_id: int) -> None:
	folder = BASE_DIR / f"competition_{competition_id}"
	if folder.exists():
		for p in folder.rglob("*"):
			if p.is_file():
				p.unlink()
		folder.rmdir()
