# Ranger integration

Use `ranger` as normal, and see Jupyter notebook previews in place of the underlying JSON plain text!

_last tested on ranger 1.9.4_


1. If your `~/.config/ranger/` dir is empty, run `ranger --copy-config=all` to populate it w/ the defaults.

2. Add the following to `handle_extension()` in `~/.config/ranger/scope.sh` to enable panel preview:

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

3. Add the following to `~/.config/ranger/rifle.conf` to enable fullscreen preview:

```
### INSERT START
# Jupyter notebooks
ext ipynb, has nbread, label nbread, terminal = nbread "$@"
### INSERT END
```
