# Pistol integration

Pistol is a file previewer for command-line file managers like ranger and lf.

_last tested on pistol 0.5.3_

## Configuration

Add the following to `~/.config/pistol/pistol.conf`:

```
fpath .*\.ipynb$ nbread --experimental-images %pistol-filename%
```

**Note:** Pistol matches rules in order and stops at the first match. If you have other rules that might match `.ipynb` files (like a general JSON handler), make sure to place the nbread rule before them in your config file.

## Usage with file managers

### With lf

Set pistol as your previewer in `~/.config/lf/lfrc`:

```
set previewer pistol
```

### With ranger

Set pistol as your previewer in `~/.config/ranger/rc.conf`:

```
set preview_script ~/.config/pistol/pistol
set use_preview_script true
```
