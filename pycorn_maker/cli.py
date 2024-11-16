from pycorn_maker.project import Project
import click
from rich.console import Console

console = Console()


@click.group()
def cli():
	"""
	Software for quickly creating C++ projects
	"""
	pass


@cli.command()
@click.argument("project_name")
@click.option("--interactive", is_flag=True, help="Run an interactive mode")
@click.option("--cpp-standard", default="17", help="C++ standard version (default: 17)")
@click.option("--cmake-version", default="3.14", help="CMake version (default: 3.14)")
@click.option(
	"--tools",
	multiple=True,
	help="Optional tools to include: clang-tidy, cppcheck, doxygen, lcove, clang-format, codespell, conan, vcpkg",
)
def create(
	project_name: str,
	interactive: bool,
	cpp_standard: str,
	cmake_version: str,
	tools: list,
):
	if interactive:
		cpp_standard = click.prompt("Enter CPP standard (default: 17)", default='17', type=str)
		cmake_version = click.prompt("Enter CMake Version (default: 3.14)", default='3.14', type=str)

	project = Project(project_name, cpp_standard, cmake_version, tools)
	project.run()
	console.print(f"[green]Project '{project_name}' created successfully![/green]")
