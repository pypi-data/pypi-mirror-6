Manual Setup
============

Install dependencies
--------------------

All dependencies are listed in `requirements.txt`. Either install them by hand
or use pip::

    pip install -r requirements.txt

Install blogtopoid
------------------

You can either build a blogtopoid egg using setup.py to deploy, use install
blogtopoid directly::

    python setup.py install

Set up directory structure
--------------------------

Next you need to set up a few directories:

outputdir
  is where the generated blog is stored. This directory needs to either be
  web accessible, or uploaded (rsync, ftp) to a web host.

inputdir
  is where you put your posts source files. filenames need to be
  "YYYYMMDD post title.md" (or .rst)

pagesdir
  is where you put your static pages (e.g. about, contact, ...)

styledir
  contains all files needed to style your blog: CSS, fonts, graphic elements.

templatedir
  contains the blogs templates. see :doc:`templates` for details.

Configure blogtopoid
--------------------

blogotpoid looks for a configuration file in the following places:

* current directory, blogtopoid.config
* user home directory, .blogtopoid.config
* /etc/blogtopoid.config

Create one of those according to `blogtopoid.config.example`.

GIT hook
--------

If you want to automatically deploy your blog from git install a post-receive
hook that generates the blog in your repository.

example (with blogotpoid + dependencies installed in a virtualenv)::

    #!/bin/sh

    # dir where the checked out project lives on the server
    CHECKOUT_DIR=/home/chris/blog
    # virtualenv directory to use
    VENV_DIR=$CHECKOUT_DIR/venv

    # cd into checkout dir, git pull, generate blog
    cd $CHECKOUT_DIR
    GIT_DIR=$CHECKOUT_DIR/.git
    GIT_WORK_TREE=$CHECKOUT_DIR /usr/bin/git pull -v
    $VENV_DIR/bin/blogtopoid
