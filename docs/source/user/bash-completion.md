### Bash Completion

Font Bakery comes with a minimal Bash completion script to help you to type the subcommands that follow directly after the `fontbakery` command by hitting the tab key.

There's no special completion support for the arguments of the subcommands yet.

First, install `bash-completion` package. And then run:

    $ source path-to/fontbakery/bin/bash-completion

To install it permanently, copy or symlink the `path-to/fontbakery/bin/bash_completion` file into your `bash_completion.d` directory as `fontbakery`.
Eg for GNU+Linux,

    ln -s path-to/fontbakery/bin/bash_completion /etc/bash_completion.d/fontbakery

On macOS the `bash_completion.d` directory may be `/sw/etc/bash_completion.d/fontbakery` or `/opt/local/etc/bash_completion.d/fontbakery`

Then restart your Terminal or bash shell.
