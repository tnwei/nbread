import os
import subprocess


def check_terminal_supports_sixel() -> bool:
    term = os.environ.get("TERM", "")
    term_program = os.environ.get("TERM_PROGRAM", "")

    # Known sixel-capable terminals
    sixel_terms = ["xterm", "mlterm", "foot", "wezterm", "konsole", "contour"]

    for sixel_term in sixel_terms:
        if sixel_term in term.lower() or sixel_term in term_program.lower():
            return True

    return False


def check_sixel_renderer_available() -> bool | str:
    # Checks for chafa
    result = subprocess.run(["which", "chafa"])
    if result.returncode == 0:
        fpath = result.stdout.decode("ascii").strip()
        return fpath

    return False


def handle_image_output(image_data: str) -> bytes | None:
    if not check_terminal_supports_sixel():
        return None

    sixel_exec_path = check_sixel_renderer_available()

    if bool(sixel_exec_path) is False:
        return None

    else:
        # TODO: Sixel rendering code
        return b"placeholder-text-to-print"
