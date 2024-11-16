from pathlib import Path


def create_directory(path: Path):
	"""Создает директорию, если она не существует."""
	Path(path).mkdir(parents=True, exist_ok=True)
