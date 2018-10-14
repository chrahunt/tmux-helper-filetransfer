# tmux-helper-filetransfer

Transfer files to filesystem of host accessible via tmux.

# Usage

In `tmux.conf`:

```
bind-key Q run-shell " \
    /path/to/.venv/bin/python \
    -m tmux_helper_filetransfer \
    --pane-id '#{pane_id}' \
    --tmux-exe /proc/#{pid}/exe \
    --tmux-socket '#{socket_path}' \
    --quiet \
    /path/to/dotfiles"
```

This transfers `/path/to/dotfiles` to the current directory in the remote
shell. To take other actions (like `cd`ing to a specific directory before
transferring files), then run a shell script that executes the
helper inside.

# Requirements

The target pane can be hosting a terminal on the local host or on a remote
host (accessed via e.g. ssh).

The target pane's shell must be able to successfully execute
`uudecode | gunzip -c - | tar xf -`.

The target pane's shell must be in insert mode (not vi-command mode).

# Limitations

Some or all of these may be possible to overcome.

1. Currently the local file processing requires that the entire file be held in
   memory at the same time, plus extra when both the tar and compressed objects
   are in scope - we would need streaming for the tar creation the compression
   and uuencoding.
2. `uuencode` expands the compressed bytes at least 33%.
3. Tmux itself is not responsive while executing the subprocess. - we could run
   a background process instead of blocking.
4. No progress indication - a periodic `display-message` would be the first
   thing to try.
5. No ability to cancel an in-progress transfer - if spawning a background
   process then giving the cli the ability to communicate via e.g. unix socket
   could be a good way to go.

# Releasing

```
python setup.py sdist
# for testing
twine upload --repository testpypi dist/*
twine upload --repository pypi dist/*
```
