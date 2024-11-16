import os
from pathlib import Path
from pycorn_maker.templates import TEMPLATES
from pycorn_maker.cmake_modules import CMAKE_MODULES
from pycorn_maker.utils import create_directory
from pycorn_maker.validators import validate_project_name
from pycorn_maker.tools import Tools


class Project:
	"""
	This class describes a project.
	"""

	def __init__(self, project_name: str, cpp_standard: str, cmake_version: str, tools: list):
		"""
		Constructs a new instance.

		:param      project_name:   The project name
		:type       project_name:   str
		:param      cpp_standard:   The cpp standard
		:type       cpp_standard:   str
		:param      cmake_version:  The cmake version
		:type       cmake_version:  str
		:param      tools:          The tools
		:type       tools:          list
		"""
		validate_project_name(project_name)
		self.project_name = project_name
		self.cpp_standard = cpp_standard
		self.cmake_version = cmake_version
		self.tools = Tools(tools)
		self.base_dir = Path(project_name)
		self.cmake_dir = self.base_dir / 'cmake'
		self.src_dir = self.base_dir / 'src'
		self.test_dir = self.base_dir / 'tests'
		self.modules_dir = self.cmake_dir / 'modules'
		self.include_dir = self.base_dir / 'include'

		create_directory(self.base_dir)
		create_directory(self.cmake_dir)
		create_directory(self.src_dir)
		create_directory(self.modules_dir)
		create_directory(self.test_dir)
		create_directory(self.include_dir)

	def create_files(self):
		"""
		Creates files.
		"""
		self._create_library_or_executable()

		self.tools.configure_tools(self.base_dir)

	def _create_basic_templates(self):
		"""
		Creates basic templates.
		"""
		self._copy_template('CMakeLists.txt', self.base_dir / 'CMakeLists.txt')
		self._copy_template('README.md', self.base_dir / 'README.md')
		self._copy_template('BUILDING.md', self.base_dir / 'BUILDING.md')
		self._copy_template('CMakePresets.json', self.base_dir / 'CMakePresets.json')
		self._copy_template('CMakeUserPresets.json', self.base_dir / 'CMakeUserPresets.json')
		self._copy_template('.clang-format', self.base_dir / '.clang-format')
		self._copy_template('.clang-tidy', self.base_dir / '.clang-tidy')
		self._copy_template('build.sh', self.base_dir / 'build.sh')
		self._copy_template('format-code.py', self.base_dir / 'format-code.py')

		for name in CMAKE_MODULES.keys():
			self._copy_template(name, self.modules_dir / name, templates=CMAKE_MODULES)

	def _create_library_or_executable(self):
		"""
		Creates a library or executable.
		"""
		self._create_basic_templates()
		self._copy_template('my_library.hpp', self.base_dir / 'include' / 'my_library.hpp')
		self._copy_template('main.cpp', self.base_dir / 'src' / 'main.cpp')

	def _copy_template(self, template_name: str, destination: Path, templates = TEMPLATES):
		"""
		Copy template

		:param      template_name:  The template name
		:type       template_name:  str
		:param      destination:    The destination
		:type       destination:    Path
		"""
		template_content = templates.get(template_name)

		if template_content:
			content = template_content.replace('{{project_name}}', self.project_name).replace('{{cpp_standard}}', self.cpp_standard).replace('{{cmake_version}}', self.cmake_version)

			with open(destination, 'w', encoding='utf-8') as dest_file:
				dest_file.write(content)

	def run(self):
		"""
		Run project creation
		"""
		self.create_files()
