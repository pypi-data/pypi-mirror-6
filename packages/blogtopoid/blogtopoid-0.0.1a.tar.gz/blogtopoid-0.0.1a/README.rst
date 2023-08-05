blogtopoid
==========

This is pre-alpha. Most things don't work yet.

blogtopoid is a blog generator - it takes a bunch of posts, renders them
to HTML and saves them to a web directory.

Structure
=========

Work flow:

-  take all documents from pagesdir, render them and save them to outputdir/.
-  take all posts from inputdir, render and save to outputdir/YYYY/mm/dd/. 
   post filename must be "YYYYMMDD post title.ext".
-  generate index.html linking all posts.
-  generate rss feed including all posts.
-  generate listing pages for all used tags.
-  pack and copy style files from style/ to outputdir/style/.

Post formats
============

Currently posts and pages can either be markdown2 or reStructuredText.

In posts and pages ``{{blogurl}}`` gets replaced with blogurl from
config, in style files ``{{styleurl}}`` with blogurl/style.

Usage
=====

-  pip install blogtopoid
-  run blogtopoid --quickstart
-  run blogtopoid
-  see post-receive.example for automatically deploying from git
   commits.

TODO
====

-  don't pregenerate listings (index, tag-pages), move to template.
-  TEST!
-  make a shipable default template
-  implement --post
-  check hashes
-  paginate index (not relevant with current index)
