Tod
============

Central management of your personal configs using a git repository and symlinks.


Installation
============

Install the client::

    pip install tod


Point to your configuration repo::

    # Environment variables will be expanded.
    export $TOD_FILE_REPO='/path/to/your/repo'


Config Repo Layout
==================

The Config Repo format is as follows::

    Root Config Directory
    ├── files
    │   ├── file_a
    │   ├── ...
    │   └── file_z
    └── mapping.ini

The `mapping.ini` file maps configs from the `files` directory to their installation path.
Currently everything lives under a `default` section, and all mappings are of the form `CONFIG_FILE: INSTALL_PATH`.
An example config is shown below.  It would map `$REPO/files/vimrc` to `~/.vimrc`, and `REPO/files/tmux.conf` to `~/.tmux.conf`::

    [default]
    vimrc: ~/.vimrc
    tmux.conf: ~/.tmux.conf.

    [git]
    gitconfig: ~/.gitconfig


Usage
=====


See the current status of the of all sections::

    tod status


See the current status of a single section::

    tod status -s SECTION


Link a single config into the system::

    tod link -S SECTION -n NAME


Link a single section into the system::

    tod link -s SECTION -a


Link all sections into the system::

    tod link -a


Unlink a single config from the system::

    tod unlink -s SECTION -n NAME


Unlink a all sections from the system::

    tod unlink -a


TODO
====
* Add section inheritance
  * example:  `[osx]` inherits all of `[vim]`, `[git]`, and `[zsh]`
* Add more helpers to initiliaze a system quickly
  * `tod init -g GIT_URI -s SECTION` would clone the specified git repo then link the specified section into the system.
* Force linking.
  * move the conflicting files to a backup location, then link as needed.
