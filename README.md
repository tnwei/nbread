# nb-read

Snappy previews of Jupyter notebooks from the command line, with ranger integration.

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
usage: nbread [-h] [--paging PAGING] filename

positional arguments:
  filename

optional arguments:
  -h, --help       show this help message and exit
  --paging PAGING  Specify when to use the pager [auto/never/always], defaults to auto
```

## Setup

Installation: `pipx install git+https://github.com/tnwei/nbread`. 

## Ranger integration

Use `ranger` as normal, and see Jupyter notebook previews in place of the underlying JSON plain text!

Do the following for `ranger` integration:

If your `~/.config/ranger/` dir is empty, run `ranger --copy-config=all` to populate it w/ the defaults.

Enabling panel preview when a notebook is highlighted: modify `handle_extension()` in `~/.config/ranger/scope.sh`:

```bash
handle_extension(){
    case "${FILE_EXTENSION_LOWER}" in
        ### INSERT START
        ipynb)
        ¦   # Jupyter notebook previewer
            nbread "${FILE_PATH}" && { dump | trim; exit 5; } || exit 2;;
        ### INSERT END

        # Archive extensions:
```

Enabling fullscreen preview in terminal when a notebook is selected: add the following to `~/.config/ranger/rifle.conf`:

```
### INSERT START
# Jupyter notebooks
ext ipynb  = nbread "$1" --pager
### INSERT END
```

Last tested on ranger 1.9.3, requires `less` installed.

## Appreciation

Code heavily based on [Textualize/rich-cli](https://github.com/Textualize/rich-cli)'s notebook pretty printing. This is pretty much `rich <notebook.ipynb>` with some speed tweaks and standalone packaging for convenience.

