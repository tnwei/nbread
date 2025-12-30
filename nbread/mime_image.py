def check_terminal_supports_sixel() -> bool:
    # TODO
    return False


def check_sixel_renderer_available() -> bool:
    # TODO
    return False


def check_supports_sixel() -> bool:
    if not check_terminal_supports_sixel():
        return False
    if not check_sixel_renderer_available():
        return False

    return True


def handle_image_output(image_data: str) -> str | None:
    if not check_supports_sixel():
        return None
    else:
        # TODO: Sixel rendering code
        return "placeholder-text-to-print"
