import argparse

from typing import Optional, Tuple, Any
import subprocess
import sys
import os
import traceback

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
        raise ValueError("cannot specify both head and tail")
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
    paging: str,
) -> RenderableType:
    use_pager = True if (paging == "auto") or (paging == "always") else False
    try:
        if use_pager is True:
            # Make sure `less` exists
            if not os.path.exists("/usr/bin/less"):
                raise FileNotFoundError(
                    "/usr/bin/less not found, either run with `--pager never` or install `less`"
                )

            # Open a subprocess to less
            if paging == "auto":
                proc = subprocess.Popen(
                    [
                        "/usr/bin/less",
                        "-R",  # This is for colour
                        "-F",  # This is for exiting if less than one page!
                        "-K",  # This is for clecan exit if Ctrl-C is called instead of exiting the colon (:) menu
                    ],
                    stdin=subprocess.PIPE,
                    universal_newlines=True,
                    stdout=sys.stdout,
                )
            elif paging == "always":
                proc = subprocess.Popen(
                    [
                        "/usr/bin/less",
                        "-R",  # This is for colour
                        # "-F", # This is for exiting if less than one page, can't use since it blocks less from dumping to stdout
                        "-K",  # This is for clecan exit if Ctrl-C is called instead of exiting the colon (:) menu
                    ],
                    stdin=subprocess.PIPE,
                    universal_newlines=True,
                    stdout=sys.stdout,
                )
            else:
                ValueError("Accepted options for --paging are [auto/never/always]")

            def pager_cleanup():
                try:
                    # Diving into the intricacies of how this works isn't what I had in mind
                    # Just gonna follow codein std lib
                    # ref: https://github.com/python/cpython/blob/b1e314ab9f8c3a2b53c7179674811f9c79328ce7/Lib/subprocess.py#L1039
                    proc.stdin.close()
                except OSError:
                    pass

                if proc.poll() is None:
                    proc.terminate()
                    proc.wait()

        console = Console(color_system="auto")

        def wrapped_print(text):
            text = Padding(text, (0, 4))
            if use_pager:
                with console.capture() as capture:
                    console.print(text)

                captured_text = capture.get()
                proc.stdin.write(captured_text)
                proc.stdin.flush()
            else:
                console.print(text)

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
                wrapped_print("")

            if "execution_count" in cell:
                execution_count = cell["execution_count"] or " "
                wrapped_print(
                    f"[green]In [[#66ff00]{execution_count}[/#66ff00]]:[/green]"
                )

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
                        word_wrap=True,
                        line_range=line_range,
                    ),
                    border_style="dim",
                )
            elif cell["cell_type"] == "markdown":
                renderable = Markdown(source, code_theme=theme, hyperlinks=hyperlinks)
            else:
                renderable = Text(source)
            new_line = True

            wrapped_print(renderable)

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

                wrapped_print(renderable)

        if use_pager:
            # Close stdin
            proc.stdin.close()
            # Wait for user to be done w/ the pager
            # W/o this line, stdin bugs out and shows nothing after run
            proc.wait()

    except BrokenPipeError:
        # Broken pipe happens if we quit from the pager
        # Doesn't happen if we've scrolled till end though
        if use_pager:
            pager_cleanup()

    except KeyboardInterrupt:
        # The pager will handle exit on its own due to the -K flag, no need cleanup
        pass

    except Exception as e:
        # Print traceback
        traceback.print_exc()
        # Wrapped everything in try-except just to clean up pager exit gracefully
        if use_pager:
            pager_cleanup()

    return None


def run():
    parser = argparse.ArgumentParser(
        # prog = 'ProgramName',
        # description = 'What the program does',
        # epilog = 'Text at the bottom of help'
    )
    parser.add_argument("filename")
    parser.add_argument(
        "--paging",
        default="auto",
        help="Specify when to use the pager [auto/never/always], defaults to auto",
    )
    args = parser.parse_args()

    if args.paging not in ["auto", "never", "always"]:
        raise ValueError("Accepted options for --paging are [auto/never/always]")

    _ = render_ipynb_jit(
        args.filename,
        theme="ansi_dark",
        hyperlinks=False,
        lexer="",
        head=None,
        tail=None,
        line_numbers=False,
        guides=False,
        paging=args.paging,
    )


if __name__ == "__main__":
    run()
