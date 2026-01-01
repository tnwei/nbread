# nbread

Snappy previews of Jupyter notebooks from the command line

<p align="center">
  <img width="800" src="https://raw.githubusercontent.com/tnwei/nbread/main/nbread-cast.svg">
</p>

## Use case

+ Read notebooks using just the terminal, don't need to spin up a Jupyter Notebook / Lab instance
+ Read superlarge notebooks without chugging Jupyter Notebook / Lab

## Usage

Run `nbread notebook.ipynb` for notebook preview in terminal.

```bash
$ nbread --help
usage: nbread [-h] [--no-pager] [--experimental-images] filename

positional arguments:
  filename

optional arguments:
  -h, --help              show this help message and exit
  --no-pager              Disable pager and print directly to stdout
  --experimental-images   Enable experimental Sixel image rendering (disables pager,
                          requires compatible terminal and chafa)

Paging: Defaults to 'less' with auto-exit. Override with $PAGER env var or
disable with --no-pager. Set PAGER='' to disable paging via environment.
```

Try it out with the notebooks bundled in `tests/`!

### Experimental: Image Support

`nbread` supports rendering images in notebooks using Sixel graphics. This feature is experimental and requires:

- A Sixel-compatible terminal (e.g., `xterm`, `mlterm`, `foot`, `wezterm`, `konsole`, `contour`). Check [Are We Sixel Yet](https://www.arewesixelyet.com/) for a latest up-to-date list
- `chafa` installed (install via your package manager: `sudo apt install chafa`, `brew install chafa`, `sudo dnf install chafa` etc.)

To enable image rendering:

```bash
nbread --experimental-images notebook.ipynb
```

**Note:** The `--experimental-images` flag automatically disables the pager since Sixel graphics don't work correctly in pagers. For notebooks with images, you'll see the full output printed directly to your terminal.

## Setup

One of the following:

`pip install git+https://github.com/tnwei/nbread`

`pipx install git+https://github/com/tnwei/nbread`

`uv tool install git+https://github/com/tnwei/nbread`

## Integrations

- [ranger](docs/ranger.md)
- [lf](docs/lf.md)


## Appreciation

Code heavily based on [Textualize/rich-cli](https://github.com/Textualize/rich-cli)'s notebook pretty printing.
