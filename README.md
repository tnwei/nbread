# nb-read

I'm trying to figure out getting snappy previews of Jupyter notebooks from the command line, and ultimately in `ranger`. Here are my efforts.

## Usage

Run `nbread notebook.ipynb` for notebook preview in terminal, or just use `ranger` as normal..

## Setup

Installation: `pipx install g+https://github.com/tnwei/nbread`. 

Do the following for `ranger` integration:

If your `~/.config/ranger/` dir is empty, run `ranger --copy-config=all` to populate it w/ the defaults.

Enabling panel preview when a notebook is highlighted: modify `handle_extension()` in `~/.config/ranger/scope.sh`:

```bash
handle_extension(){
    case "${FILE_EXTENSION_LOWER}" in
        ### INSERT START
        ipynb)
        ¦   # Jupyter notebook previewer
            nbread "${FILE_PATH}" --forcecolor && { dump | trim; exit 5; } || exit 2;;
        ### INSERT END

        # Archive extensions:
```

Enabling fullscreen preview in terminal when a notebook is selected: add the following to `~/.config/ranger/rifle.conf`:

```
### INSERT START
# Jupyter notebooks
ext ipynb  = nbread --forcecolor "$1" --pager
### INSERT END
```

Last tested on ranger 1.9.3, requires `less` installed.



## Appreciation

Code heavily based on [Textualize/rich-cli](https://github.com/Textualize/rich-cli)'s notebook pretty printing.

