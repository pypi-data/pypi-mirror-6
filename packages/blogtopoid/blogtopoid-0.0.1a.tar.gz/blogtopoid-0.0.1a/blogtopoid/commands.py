""" commands for blogtopoid script
"""
from __future__ import unicode_literals
from __future__ import absolute_import

import os
import sys
import codecs
import ConfigParser
import pkg_resources

from .blogtopoid import (Config, generate_index, generate_feed,
                         generate_tag_indeces, prepare_style, tags, Post, Page)


def quickstart():
    """ ask for all configuration options and write example files.
    """
    # read config template
    config_file = pkg_resources.resource_stream(
        __name__,
        'example/blogtopoid.config.example',
    )

    # query user for config options
    config = ConfigParser.SafeConfigParser()
    config.readfp(config_file)
    for section in config.sections():
        for option in config.options(section):
            answer = raw_input(
                "{} [default: {}] = ".format(option,
                                             config.get(section, option))
            )
            if answer:
                config.set(section, option, answer)
    config.write(codecs.open('blogtopoid.config', 'w', 'utf8'))

    # make post and pages dirs
    if not os.path.exists(config.get('general', 'inputdir')):
        os.makedirs(config.get('general', 'inputdir'))
    if not os.path.exists(config.get('general', 'pagesdir')):
        os.makedirs(config.get('general', 'pagesdir'))
    if not os.path.exists(config.get('general', 'styledir')):
        os.makedirs(config.get('general', 'styledir'))
    if not os.path.exists(config.get('general', 'templatedir')):
        os.makedirs(config.get('general', 'templatedir'))

    # copy example post to inputdir/
    hw_post = pkg_resources.resource_stream(
        __name__,
        'example/19700101 example.md',
    )
    codecs.open(
        os.path.join(
            config.get('general', 'inputdir'), '19700101 example.md'
        ), 'w', 'utf8'
    ).write(hw_post.read())

    hw_image = pkg_resources.resource_stream(
        __name__,
        'example/19700101 pythonlogo.png',
    )
    open(os.path.join(
        config.get('general', 'inputdir'), '19700101 pythonlogo.png'
    ), 'wb').write(hw_image.read())

    # copy example template files
    for template_filename in ['index.html', 'page.html', 'post.html']:
        template_file = pkg_resources.resource_stream(
            __name__,
            'example/{}'.format(template_filename),
        )
        codecs.open(os.path.join(
            config.get('general', 'templatedir'), template_filename
        ), 'w', 'utf8').write(template_file.read())

    # done setting up
    sys.exit(0)


def post():
    """ ask for YAML front-matter options, create empty post
    and start editor
    """
    print('not yet implemented')
    sys.exit(1)


def generate():
    """ generate HTML
    """
    config = Config()

    pages = []
    for infile in os.listdir(unicode(config.pagesdir)):
        if os.path.splitext(infile)[1].lower() in config.supported_blogtypes:
            page = Page(infile)
            pages.append(page)
    for page in pages:
        page.render(pages)

    posts = []
    for infile in os.listdir(unicode(config.inputdir)):
        if os.path.splitext(infile)[1].lower() in config.supported_blogtypes:
            post = Post(infile)
            # if hashstore.get(infile) == post.hash:
            #     print("already processed")
            #     continue

            posts.append(post)
            # hashstore.set(infile, post.hash)

    # sort posts by publish date
    posts.sort(key=lambda p: p.date, reverse=True)

    # render post htmls
    for post in posts:
        post.render(pages)

    # generate index from index.md
    generate_index(posts, pages)

    # generate rss feed
    generate_feed(posts)

    # generate tag pages
    generate_tag_indeces(tags, pages)

    # copy style dir to disk
    prepare_style(
        config.outputdir,
        config.blogurl,
    )
