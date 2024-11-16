import re


def validate_project_name(project_name: str):
	"""Проверяет, что имя проекта допустимо."""
	if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', project_name):
		raise ValueError("Invalid project name. Must start with a letter or underscore and contain only letters, digits, and underscores.")
