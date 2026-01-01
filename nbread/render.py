import os
import shlex
import subprocess
import sys
import traceback
from typing import Any, Optional, Tuple

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.markdown import Markdown, TextElement
from rich.padding import Padding
from rich.syntax import Syntax
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


class OutputWriter:
    """Context manager for writing output either to a pager or directly to console."""

    def __init__(self, use_pager: bool, pager_cmd: Optional[str] = None):
        self.use_pager = use_pager
        self.proc = None
        self.pager_cmd = pager_cmd

    def __enter__(self):
        if self.use_pager:
            # Determine which pager to use
            if self.pager_cmd is not None:
                # Use custom pager from $PAGER
                pager_parts = shlex.split(self.pager_cmd)
                self.proc = subprocess.Popen(
                    pager_parts,
                    stdin=subprocess.PIPE,
                    universal_newlines=True,
                    stdout=sys.stdout,
                )
            else:
                # Use default less with our preferred flags
                # Make sure `less` exists
                if not os.path.exists("/usr/bin/less"):
                    raise FileNotFoundError(
                        "/usr/bin/less not found, either run with `--no-pager` or install `less`"
                    )

                # Open a subprocess to less with auto-exit if content fits on screen
                self.proc = subprocess.Popen(
                    [
                        "/usr/bin/less",
                        "-R",  # Enable color output
                        "-F",  # Auto-exit if less than one page
                        "-K",  # Clean exit on Ctrl-C
                    ],
                    stdin=subprocess.PIPE,
                    universal_newlines=True,
                    stdout=sys.stdout,
                )
        return self

    def write(self, renderable: RenderableType, console: Console):
        """Write renderable to either pager or console."""
        if self.use_pager:
            # Capture and pipe to pager
            with console.capture() as capture:
                console.print(renderable)
            captured_text = capture.get()
            self.proc.stdin.write(captured_text)
            self.proc.stdin.flush()
        else:
            # Direct print to console
            console.print(renderable)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.use_pager and self.proc:
            try:
                # Diving into the intricacies of how this works isn't what I had in mind
                # Just gonna follow codein std lib
                # ref: https://github.com/python/cpython/blob/b1e314ab9f8c3a2b53c7179674811f9c79328ce7/Lib/subprocess.py#L1039
                self.proc.stdin.close()
            except OSError:
                pass

            if self.proc.poll() is None:
                self.proc.terminate()
                self.proc.wait()


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
    use_pager: bool,
    pager_cmd: Optional[str] = None,
    enable_images: bool = False,
) -> RenderableType:
    try:
        if use_pager:
            # Determine which pager to use
            if pager_cmd is not None:
                # Use custom pager from $PAGER
                pager_parts = shlex.split(pager_cmd)
                proc = subprocess.Popen(
                    pager_parts,
                    stdin=subprocess.PIPE,
                    universal_newlines=True,
                    stdout=sys.stdout,
                )
            else:
                # Use default less with our preferred flags
                # Make sure `less` exists
                if not os.path.exists("/usr/bin/less"):
                    raise FileNotFoundError(
                        "/usr/bin/less not found, either run with `--no-pager` or install `less`"
                    )

                # Open a subprocess to less with auto-exit if content fits on screen
                proc = subprocess.Popen(
                    [
                        "/usr/bin/less",
                        "-R",  # Enable color output
                        "-F",  # Auto-exit if less than one page
                        "-K",  # Clean exit on Ctrl-C
                    ],
                    stdin=subprocess.PIPE,
                    universal_newlines=True,
                    stdout=sys.stdout,
                )

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
            if use_pager:
                with console.capture() as capture:
                    console.print(text)

                captured_text = capture.get()
                proc.stdin.write(captured_text)
                proc.stdin.flush()
            else:
                console.print(text)

        import json

        from rich.console import Group
        from rich.syntax import Syntax

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

            source = "".join(cell["source"])

            if cell["cell_type"] == "code":
                num_lines = len(source.splitlines())
                line_range = _line_range(head, tail, num_lines)

                # Create labeled separator
                execution_count = cell.get("execution_count", " ") or " "
                label = f"── Code [{execution_count}] "
                separator_width = console.width - 8 - len(label)
                separator = Text(label + "─" * separator_width, style="dim")

                renderable = Group(
                    separator,
                    Syntax(
                        source,
                        lexer,
                        theme=theme,
                        line_numbers=line_numbers,
                        indent_guides=guides,
                        word_wrap=True,
                        line_range=line_range,
                    ),
                )
            elif cell["cell_type"] == "markdown":
                renderable = Markdown(source, code_theme=theme, hyperlinks=hyperlinks)

            else:
                renderable = Text(source)

            new_line = True

            wrapped_print(renderable)

            # Track if we've printed the Out[] label for this cell
            printed_out_label = False

            for output in cell.get("outputs", []):
                output_type = output["output_type"]

                # Print Out[X] label once before first output
                # NOTE: In Jupyter GUI/nbformat convention, Out[X] should only appear
                # for execute_result outputs (the return value of the last expression).
                # Stream outputs (print statements), errors, and display_data don't get
                # the Out[] label in the GUI. However, for terminal readability, we
                # intentionally show Out[X] once per cell's output section to provide
                # clear visual separation between code and outputs, regardless of type.
                if not printed_out_label and output_type in [
                    "stream",
                    "error",
                    "execute_result",
                    "display_data",
                ]:
                    execution_count = cell.get("execution_count", " ") or " "
                    out_label = Text.from_markup(
                        f"\n[red]Out[[#ee4b2b]{execution_count}[/#ee4b2b]]:[/red]\n"
                    )
                    wrapped_print(out_label)
                    printed_out_label = True

                if output_type == "stream":
                    renderable = Text.from_ansi("".join(output["text"]))
                    renderable += Text("\n")
                    new_line = False

                elif output_type == "error":
                    renderable = Text.from_ansi("\n".join(output["traceback"]).rstrip())
                    new_line = True

                elif output_type == "execute_result":
                    data = output["data"].get("text/plain", "")
                    if isinstance(data, list):
                        renderable = Text.from_ansi("".join(data))
                    else:
                        renderable = Text.from_ansi(data)
                    renderable += Text("\n")
                    new_line = True

                elif output_type == "display_data":
                    data = output.get("data", {})
                    renderable = None

                    # Handle different MIME types in priority order
                    if any(mime.startswith("image/") for mime in data):
                        if enable_images:
                            for image_type in [
                                "image/png",
                                "image/jpeg",
                                "image/svg+xml",
                                "image/gif",
                            ]:
                                if image_type in data:
                                    from .mime_image import handle_image_output

                                    sixel_data = handle_image_output(
                                        data[image_type],
                                        suffix=image_type.split("/")[1],
                                    )
                                    if sixel_data is None:
                                        # Print placeholder to acknowledge image
                                        renderable = Text(
                                            f"[{image_type}]", style="dim cyan"
                                        )
                                    else:
                                        # Successfully obtained sixel payload, print it
                                        print(sixel_data, end="")
                                        renderable = Text("\n")

                                    break

                                else:
                                    renderable = Text(
                                        f"[Unsupported: {image_type}]", style="dim cyan"
                                    )
                        else:
                            # Images disabled by default, show placeholder
                            image_type = next(
                                mime
                                for mime in data.keys()
                                if mime.startswith("image/")
                            )
                            renderable = Text(f"[{image_type}]", style="dim cyan")

                    elif "text/html" in data:
                        from .mime_text import handle_html_output

                        renderable = handle_html_output(data["text/html"])

                    elif "text/latex" in data:
                        from .mime_text import handle_latex_output

                        renderable = handle_latex_output(data["text/latex"])

                    elif "text/markdown" in data:
                        from .mime_text import handle_markdown_output

                        renderable = handle_markdown_output(
                            data["text/markdown"], theme=theme, hyperlinks=hyperlinks
                        )

                    elif "application/json" in data:
                        import json

                        renderable = Text(
                            json.dumps(data["application/json"]), style="dim blue"
                        )

                    elif "application/javascript" in data:
                        # JavaScript can't be executed in terminal
                        renderable = Text("[JavaScript output]", style="dim cyan")

                    elif "text/plain" in data:
                        from .mime_text import handle_plain_output

                        renderable = handle_plain_output(data["text/plain"])

                    else:
                        # Unknown MIME type
                        mime_types = ", ".join(data.keys())
                        renderable = Text(
                            f"[Unsupported output: {mime_types}]", style="dim red"
                        )

                    if renderable:
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
