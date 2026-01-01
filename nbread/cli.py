import argparse
import os

from .render import render_ipynb_jit


def run():
    parser = argparse.ArgumentParser(
        description="Snappy previews of Jupyter notebooks from the command line",
        epilog="Paging: Defaults to 'less' with auto-exit. Override with $PAGER env var or disable with --no-pager. Set PAGER='' to disable paging via environment.",
    )
    parser.add_argument("filename")
    parser.add_argument(
        "--no-pager",
        action="store_true",
        help="Disable pager and print directly to stdout",
    )
    parser.add_argument(
        "--experimental-images",
        action="store_true",
        help="Enable experimental Sixel image rendering (disables pager, requires compatible terminal and chafa)",
    )
    args = parser.parse_args()

    # Determine paging behavior following Git's approach:
    # 1. --experimental-images flag disables pager (Sixel doesn't work in pagers)
    # 2. --no-pager flag takes precedence
    # 3. $PAGER environment variable (empty string means no paging)
    # 4. Default to auto with less
    pager_cmd = None
    use_pager = True

    if args.experimental_images:
        # Images require direct output
        use_pager = False
    elif args.no_pager:
        use_pager = False
    else:
        env_pager = os.environ.get("PAGER")
        if env_pager == "":
            # Empty string explicitly disables paging
            use_pager = False
        elif env_pager is not None:
            # Use the custom pager
            pager_cmd = env_pager

    _ = render_ipynb_jit(
        args.filename,
        theme="ansi_dark",
        hyperlinks=False,
        lexer="",
        head=None,
        tail=None,
        line_numbers=False,
        guides=False,
        use_pager=use_pager,
        pager_cmd=pager_cmd,
        enable_images=args.experimental_images,
    )


if __name__ == "__main__":
    run()
