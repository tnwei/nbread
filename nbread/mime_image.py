import os
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


def render_sixel_chafa(image_data: str) -> bytes:
    return b"placeholder-text-to-print"


def handle_image_output(image_data: str) -> bytes | None:
    if not check_terminal_supports_sixel():
        return None

    renderer = check_sixel_renderer_available()

    if renderer is False:
        return None

    else:
        if renderer == SixelRenderer.CHAFA:
            return render_sixel_chafa(image_data)
        else:
            # Not implemented yet!
            return None
