# nb-read

I'm trying to figure out getting snappy previews of Jupyter notebooks from the command line, and ultimately in `ranger`. Here are my efforts.

## Usage

Run `nbread notebook.ipynb` for notebook preview in terminal, or just use `ranger` as normal..

## Setup

Installation: `pipx install g+https://github.com/tnwei/nbread`. 

Do the following for `ranger` integration:

Enabling panel preview when a notebook is highlighted: modify `~/.config/ranger/scope.sh`:

```bash
case "$extension" in
    ### INSERT START
    ipynb)
    ¦   # Jupyter notebook previewer
        nbread "$path" --forcecolor && { dump | trim; exit 5; } || exit 2;;
    ### INSERT END

    # Archive extensions:
```

Enabling fullscreen preview in terminal when a notebook is selected: modify `~/.config/ranger/rifle.conf`:

```
### INSERT START
# Jupyter notebooks
ext ipynb  = nbread --forcecolor "$1" | "$PAGER" -R
### INSERT END
```

Last tested on ranger-stable 1.8.1, requires `less` installed.



## Appreciation

Code heavily based on [Textualize/rich-cli](https://github.com/Textualize/rich-cli)'s notebook pretty printing.

