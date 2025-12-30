from rich.markdown import Markdown
import html2text


def handle_html_output(html_data: str) -> tuple[Any, bool, bool]:
    if isinstance(html_data, list):
        html_data = "".join(html_data)

    h = html2text.HTML2Text()
    h.ignore_links = False  # Keep links
    h.body_width = 0  # Don't wrap text, let rich handle
    markdown_text = h.handle(html_data)

    # Return as Rich Markdown renderable
    renderable = Markdown(markdown_text, hyperlinks=False)

    # renderable, new_line, skip
    return renderable, True, False
