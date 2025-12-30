from rich.markdown import Markdown, Text
from rich.console import RenderableType


def handle_html_output(html_data: str) -> RenderableType:
    import html2text

    if isinstance(html_data, list):
        html_data = "".join(html_data)

    h = html2text.HTML2Text()
    h.ignore_links = False  # Keep links
    h.body_width = 0  # Don't wrap text, let rich handle
    markdown_text = h.handle(html_data)

    # Return as Rich Markdown renderable
    return Markdown(markdown_text, hyperlinks=False)


def handle_latex_output(latex_content: str) -> RenderableType:
    # Show raw LaTeX source for now
    if isinstance(latex_content, list):
        latex_content = "[LaTeX output]\n" + "".join(latex_content)
    return Text(latex_content, style="dim magenta")


def handle_markdown_output(
    md_content: str, theme: str, hyperlinks: bool
) -> RenderableType:
    # Render markdown directly
    if isinstance(md_content, list):
        md_content = "".join(md_content)

    return Markdown(md_content, code_theme=theme, hyperlinks=hyperlinks)


def handle_plain_output(text_content: str) -> RenderableType:
    # Fallback to plain text
    if isinstance(text_content, list):
        return Text.from_ansi("".join(text_content))
    else:
        return Text.from_ansi(text_content)
