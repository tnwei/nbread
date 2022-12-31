import argparse

from typing import Optional, Tuple, Any

from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.markdown import Markdown, TextElement
from rich.padding import Padding
from rich.syntax import Syntax
from rich.markup import escape
from rich.text import Text


class CodeBlock(TextElement):
    """A code block with syntax highlighting."""

    style_name = "markdown.code_block"

    @classmethod
    def create(cls, markdown: "Markdown", node: Any) -> "CodeBlock":
        node_info = node.info or ""
        lexer_name = node_info.partition(" ")[0]
        return cls(lexer_name or "default", markdown.code_theme)

    def __init__(self, lexer_name: str, theme: str) -> None:
        self.lexer_name = lexer_name
        self.theme = theme

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        code = str(self.text).rstrip()
        syntax = Syntax(code, self.lexer_name, theme=self.theme, word_wrap=True)
        yield Padding(syntax, (0, 4))


Markdown.elements["code_block"] = CodeBlock


def read_resource(path):
    with open(path, "rt", encoding="utf8", errors="replace") as resource_file:
        text = resource_file.read()
    return text


def _line_range(
    head: Optional[int], tail: Optional[int], num_lines: int
) -> Optional[Tuple[int, int]]:
    if head and tail:
        on_error("cannot specify both head and tail")
    if head:
        line_range = (1, head)
    elif tail:
        start_line = num_lines - tail + 2
        finish_line = num_lines + 1
        line_range = (start_line, finish_line)
    else:
        line_range = None
    return line_range


def render_ipynb_jit(
    resource: str,
    theme: str,
    hyperlinks: bool,
    lexer: str,
    head: Optional[int],
    tail: Optional[int],
    line_numbers: bool,
    guides: bool,
    no_wrap: bool,
    force_color: bool,
) -> RenderableType:

    color_system = "auto"
    if force_color is True:
        color_system = "standard"

    console = Console(color_system=color_system)

    import json
    from rich.syntax import Syntax
    from rich.console import Group
    from rich.panel import Panel

    notebook_str = read_resource(resource)
    notebook_dict = json.loads(notebook_str)
    lexer = lexer or notebook_dict.get("metadata", {}).get("kernelspec", {}).get(
        "language", ""
    )

    renderable: RenderableType
    new_line = True

    for cell in notebook_dict["cells"]:
        if new_line:
            console.print("")

        if "execution_count" in cell:
            execution_count = cell["execution_count"] or " "
            console.print(f"[green]In [[#66ff00]{execution_count}[/#66ff00]]:[/green]")

        source = "".join(cell["source"])
        if cell["cell_type"] == "code":
            num_lines = len(source.splitlines())
            line_range = _line_range(head, tail, num_lines)
            renderable = Panel(
                Syntax(
                    source,
                    lexer,
                    theme=theme,
                    line_numbers=line_numbers,
                    indent_guides=guides,
                    word_wrap=not no_wrap,
                    line_range=line_range,
                ),
                border_style="dim",
            )
        elif cell["cell_type"] == "markdown":
            renderable = Markdown(source, code_theme=theme, hyperlinks=hyperlinks)
        else:
            renderable = Text(source)
        new_line = True

        console.print(renderable)

        for output in cell.get("outputs", []):
            output_type = output["output_type"]
            if output_type == "stream":
                renderable = Text.from_ansi("".join(output["text"]))
                new_line = False
            elif output_type == "error":
                renderable = Text.from_ansi("\n".join(output["traceback"]).rstrip())
                new_line = True
            elif output_type == "execute_result":
                execution_count = output.get("execution_count", " ") or " "
                renderable = Text.from_markup(
                    f"[red]Out[[#ee4b2b]{execution_count}[/#ee4b2b]]:[/red]\n"
                )
                data = output["data"].get("text/plain", "")
                if isinstance(data, list):
                    renderable += Text.from_ansi("".join(data))
                else:
                    renderable += Text.from_ansi(data)
                new_line = True
            else:
                continue

            console.print(renderable)

    return None


def run():
    parser = argparse.ArgumentParser(
        # prog = 'ProgramName',
        # description = 'What the program does',
        # epilog = 'Text at the bottom of help'
    )
    parser.add_argument("filename")
    parser.add_argument("--forcecolor", action="store_true", default=False)
    args = parser.parse_args()

    renderable = render_ipynb_jit(
        args.filename,
        theme="ansi_dark",
        hyperlinks=False,
        lexer="",
        head=None,
        tail=None,
        line_numbers=False,
        guides=False,
        no_wrap=True,
        force_color=args.forcecolor,
    )


if __name__ == "__main__":
    run()
