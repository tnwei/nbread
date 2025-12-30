import os
import base64
import tempfile
import subprocess
from enum import Enum


class SixelRenderer(Enum):
    CHAFA = "chafa"


def check_terminal_supports_sixel() -> bool:
    term = os.environ.get("TERM", "")
    term_program = os.environ.get("TERM_PROGRAM", "")

    # Known sixel-capable terminals
    sixel_terms = ["xterm", "mlterm", "foot", "wezterm", "konsole", "contour"]

    for sixel_term in sixel_terms:
        if sixel_term in term.lower() or sixel_term in term_program.lower():
            return True

    return False


def check_sixel_renderer_available() -> bool | SixelRenderer:
    # Checks for chafa
    result = subprocess.run(["which", "chafa"])
    if result.returncode == 0:
        return SixelRenderer.CHAFA

    return False


def render_sixel_chafa(image_data: str, suffix: str) -> str | None:
    # Dump to tempfile
    decoded = base64.b64decode(image_data)
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(decoded)
        tmp_path = tmp.name

    # Specify sixel_data in advance incase try blocks fails
    sixel_data = None
    try:
        result = subprocess.run(
            ["chafa", "--format=sixel", tmp_path], capture_output=True
        )
        if result.returncode == 0:
            sixel_data = result.stdout.decode('latin-1')
        else:
            sixel_data = None
    finally:
        os.unlink(tmp_path)

    return sixel_data


def handle_image_output(image_data: str, suffix: str) -> str | None:
    if not check_terminal_supports_sixel():
        return None

    renderer = check_sixel_renderer_available()

    if renderer is False:
        return None

    else:
        if renderer == SixelRenderer.CHAFA:
            sixel_data = render_sixel_chafa(image_data, suffix)
            return sixel_data
        else:
            # Not implemented yet!
            return None
