# lf integration

Use `lf` as normal, and see Jupyter notebook previews in place of the underlying JSON plain text!

_last tested on lf r40_


## Prerequisites

1. If your `~/.config/lf/` dir doesn't exist, create it with `mkdir -p ~/.config/lf` and initialize your config by copying `/etc/lfrc.example` from `github.com/gokechan/lf` as `~/.config/lf/lfrc`

2. (Experimental images) If you want image preview:
  - Make sure you have `set sixel true` in `~./config/lf/lfrc`

## Using a dedicated previewer / file opener

Note: If you're using `lf`, high chances are you are using a dedicated previewer / file opener. Follow their own instructions instead.

## Using your own previewer

1. Configure location of your previewer script in `~/.config/lf/lfrc` if you don't have one already:

```
+ set previewer ~/.config/lf/previewer
```

2. Modify `~/.config/lf/previewer` with the following content:

```bash
#!/bin/sh

case "$1" in
    *.ipynb)
        nbread "$1"
        ;;
    *)
        # Fallback for other file types
        cat "$1"
        ;;
esac
```

3. Make the previewer script executable:

```bash
chmod +x ~/.config/lf/previewer
```

## Using your own file opener

1. Add the following to `~/.config/lf/lfrc` to open Jupyter notebooks with `nbread`:

```
# Jupyter notebooks
cmd open ${{
    case "$f" in
        *.ipynb) nbread "$f" ;;
        *) $OPENER "$f" ;;
    esac
}}
```

2. (Experimental images) If you want image preview:
  - Modify Step 5 to use `nbread --experimental-images "$f"`
