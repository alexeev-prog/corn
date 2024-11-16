import os
from pathlib import Path


class Tools:
	"""Класс для управления конфигурацией инструментов."""

	def __init__(self, tools):
		self.tools = tools

	def configure_tools(self, base_dir: Path):
		"""Конфигурирует выбранные инструменты для проекта."""
		tools_dir = base_dir / 'tools'
		os.makedirs(tools_dir, exist_ok=True)

		if "clang-tidy" in self.tools:
			with open(tools_dir / '.clang-tidy', 'w', encoding='utf-8') as f:
				f.write("Checks: '-*,clang-analyzer-*'\nWarningsAsErrors: '*'\n")
		
		if "cppcheck" in self.tools:
			with open(tools_dir / 'cppcheck.cfg', 'w', encoding='utf-8') as f:
				f.write("enable=all\n")
		
		if "doxygen" in self.tools:
			with open(tools_dir / 'Doxyfile', 'w', encoding='utf-8') as f:
				f.write("PROJECT_NAME = {project_name}\nOUTPUT_DIRECTORY = docs\n")
		
		if "lcov" in self.tools:
			with open(tools_dir / '.lcovrc', 'w', encoding='utf-8') as f:
				f.write("genhtml --output-directory coverage\n")
		
		if "clang-format" in self.tools:
			with open(tools_dir / '.clang-format', 'w', encoding='utf-8') as f:
				f.write("BasedOnStyle: Google\nIndentWidth: 4\n")
		
		if "codespell" in self.tools:
			with open(tools_dir / '.codespellrc', 'w', encoding='utf-8') as f:
				f.write("# Codespell configuration\n")

		if "conan" in self.tools:
			with open(base_dir / 'conanfile.py', 'w', encoding='utf-8') as f:
				f.write("from conans import ConanFile\n\nclass MyConan(ConanFile):\n    name = '{project_name}'\n")
		
		if "vcpkg" in self.tools:
			with open(base_dir / 'vcpkg.json', 'w', encoding='utf-8') as f:
				f.write("{\n    'version': 3,\n    'dependencies': []\n}\n")