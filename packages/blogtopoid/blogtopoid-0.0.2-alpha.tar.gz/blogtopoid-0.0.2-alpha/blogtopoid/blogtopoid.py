"""
objects and functions of blogtopoid.
"""
from __future__ import unicode_literals
from __future__ import absolute_import

import re
import os
import sys
import json
import glob
import codecs
import shutil
import hashlib
import datetime
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

import yaml
import PyRSS2Gen
import markdown2
from cssmin import cssmin
from slugify import slugify
from docutils.core import publish_parts
from jinja2 import Environment, FileSystemLoader
from pygments.formatters.html import HtmlFormatter

from .decorators import singleton


tags = {}


@singleton
class Config(object):
    """ parse blogtopoid.config """
    def __init__(self):
        confparser = ConfigParser.SafeConfigParser()
        confparser.read([
            '/etc/blogtopoid.config',
            os.path.expanduser('~/.blogtopoid.config'),
            'blogtopoid.config',
        ])

        if not confparser.has_section('general'):
            print('please set up either /etc/blogtopid.config, {}, '
                  'or blogtopoid.config in current dir.'.format(
                      os.path.expanduser('~/.blogtopoid.config')
                  ))
            sys.exit(1)

        self.blogtitle = confparser.get('general', 'blogtitle')
        self.blogdescription = confparser.get('general', 'blogdescription')
        self.outputdir = confparser.get('general', 'outputdir')
        self.inputdir = confparser.get('general', 'inputdir')
        self.pagesdir = confparser.get('general', 'pagesdir')
        self.styledir = confparser.get('general', 'styledir')
        self.templatedir = confparser.get('general', 'templatedir')
        self.blogurl = confparser.get('general', 'blogurl')
        self.supported_blogtypes = \
            confparser.get('general', 'supported_blogtypes').split(',')
        self.mdextras = confparser.get('md', 'mdextras').split(',')


class Tag(object):
    """ a tag, with colour and posts """
    def __init__(self, name):
        self.name = name
        self.posts = []

    @property
    def colour(self):
        """ return html colour for Tag. """
        return hashlib.md5(self.name.encode('utf-8')).hexdigest()[:6]


class Post(object):
    """ all info about a blog post.

    fields:
    * body: rendered HTML body
    * filename: source filename on disk
    * extension: type of post, inferred from filename
    * date: publish date, inferred from filename
    * title: post title, inferred from filename
    * hash: hash of post source file
    * outputpath: relative part for post (e.g. 1970/01/01/)
    * outfile: full path + filename the rendered post will have
    * link: URI the post will have
    """
    def __init__(self, filename):
        config = Config()

        self.inputdir = config.inputdir
        self.body = None
        self.filename = filename
        self.extension = os.path.splitext(filename)[1].lower()
        self.date = datetime.date(int(filename[0:4]), int(filename[4:6]),
                                  int(filename[6:8]))
        self.title = os.path.splitext(filename[9:])[0]
        # self.hash = hashstore.hashfile(
        #     os.path.join(self.inputdir, filename)
        # )
        self.outputpath = os.path.join(filename[0:4], filename[4:6],
                                       filename[6:8])
        self.outfile = os.path.join(
            self.outputpath, "{}.html".format(slugify(self.title))
        )
        self.link = "{}{}".format(config.blogurl, self.outfile)
        self.tags = []

    def render(self, pages):
        """ generate post html and write to disk """
        config = Config()

        print("writing {}".format(os.path.join(config.outputdir,
                                               self.outfile)))

        # parse front matter
        re_yaml = re.compile(r'(^---\s*$(?P<yaml>.*?)^---\s*$)'
                             '?(?P<content>.*)', re.M | re.S)
        post_file = codecs.open(
            os.path.join(self.inputdir, self.filename), 'r', 'utf8',
        ).read()
        file_info = re_yaml.match(post_file)
        yamlstring = file_info.groupdict().get('yaml')
        post_yaml = yaml.load(yamlstring) if yamlstring else {}
        post_content = file_info.groupdict().get('content')

        if type(self) == Post and 'tags' in post_yaml:
            for tag_text in post_yaml.get('tags').split(','):
                if tag_text not in tags:
                    tags[tag_text] = Tag(tag_text)
                self.tags.append(tags[tag_text])
                tags[tag_text].posts.append(self)

        # make output directory for post
        outputdir = config.outputdir
        if not os.path.exists(os.path.join(outputdir, self.outputpath)):
            os.makedirs(os.path.join(outputdir, self.outputpath))

        # copy supplementary files to ouput dir
        for infile in os.listdir(unicode(self.inputdir)):
            if ((os.path.splitext(infile)[1].lower() not in
                    config.supported_blogtypes) and
                    infile[0:8] == self.date.strftime('%Y%m%d')):
                shutil.copy(
                    os.path.join(self.inputdir, infile),
                    os.path.join(outputdir, self.outputpath, infile[9:])
                )

        # load jinja2 template
        env = Environment(loader=FileSystemLoader(config.templatedir))
        post_template = env.get_template('post.html')

        # actually render post
        add_style = ''
        if self.extension == '.md':
            self.body = markdown2.markdown(
                post_content,
                extras=config.mdextras,
            )
        elif self.extension == '.rst':
            rst = publish_parts(
                post_content,
                writer_name='html'
            )
            add_style = rst['stylesheet']
            self.body = rst['html_body']
        else:
            return

        # return rendered post
        return post_template.render(
            config=config,
            post=self,
            pages=pages,
            add_style=add_style,
        )


class Page(Post):
    """ all info about a blog page.

    fields:
    * body: rendered HTML body
    * filename: source filename on disk
    * extension: type of post, inferred from filename
    * title: post title, inferred from filename
    * hash: hash of post source file
    * outfile: full path + filename the rendered post will have
    * link: URI the post will have
    """
    def __init__(self, filename):
        config = Config()

        self.inputdir = config.pagesdir
        self.body = None
        self.filename = filename
        self.extension = os.path.splitext(filename)[1].lower()
        self.title = os.path.splitext(filename)[0]
        # self.hash = hashstore.hashfile(
        #     os.path.join(self.inputdir, filename)
        # )
        self.outputpath = ''
        self.outfile = "{}.html".format(slugify(self.title))
        self.link = "{}{}".format(config.blogurl, self.outfile)


@singleton
class Hashstore(object):
    """ store file hashes in a json file """
    def __init__(self, jsonfile):
        self.filename = jsonfile
        try:
            with open(self.filename, 'r') as filehandler:
                self.store = json.load(filehandler)
        except (IOError, ValueError):
            self.store = {}

    def get(self, objname):
        """ look up saved hash for objname

        :param objname: key to look for
        :return: hash or None
        """
        if objname in self.store:
            return self.store[objname]
        else:
            return None

    def set(self, objname, objhash):
        """ save calculated hash for objname

        :param objname: key to save
        :param objhash: hash to save
        """
        self.store[objname] = objhash
        with open(self.filename, 'w') as filehandler:
            json.dump(self.store, filehandler)

    @staticmethod
    def hashfile(filename, blocksize=65536):
        """ calculate sha256 hash of a files contents.

        :param filename: file to calculate hash of
        :param blocksize: read file in chunks of blocksize
        :return: sha256 hexdigest
        """
        with open(filename, 'rb') as afile:
            hasher = hashlib.sha256()
            buf = afile.read(blocksize)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(blocksize)
            return hasher.hexdigest()


def generate_feed(posts):
    """ write feed.rss to disk

    :param posts: post objs to generate feed for.
    :type posts: list of Post
    """
    config = Config()

    rssitems = [
        PyRSS2Gen.RSSItem(
            title=post.title,
            description=post.body,
            link=post.link,
            guid=PyRSS2Gen.Guid(post.link),
            pubDate=datetime.datetime.combine(post.date,
                                              datetime.datetime.min.time()),
        ) for post in posts
    ]
    PyRSS2Gen.RSS2(
        title=config.blogtitle,
        description=config.blogdescription,
        link=config.blogurl,
        lastBuildDate=datetime.datetime.now(),
        items=rssitems
    ).write_xml(
        open(os.path.join(config.outputdir, 'feed.rss'), 'w')
    )


def generate_index(posts, pages):
    """ render index.html files contents

    :param posts: post objs to generate index for.
    :type posts: list of Post
    """
    config = Config()

    # load jinja2 template
    env = Environment(loader=FileSystemLoader(config.templatedir))
    post_template = env.get_template('index.html')

    # generate index from template
    return post_template.render(
        config=config,
        pages=pages,
        posts=posts,
    )


def prepare_style():
    """ read and process style/ directory """
    config = Config()
    # copy static files
    if not os.path.exists(os.path.join(config.outputdir, 'style')):
        os.makedirs(os.path.join(config.outputdir, 'style'))

    # copy supplementary files to ouput dir
    for filename in os.listdir(config.styledir):
        if os.path.splitext(filename)[1].lower() != '.css':
            shutil.copy(
                os.path.join(config.styledir, filename),
                os.path.join(config.outputdir, 'style')
            )

    # generate syntax highlight css and append all other CSS files
    allcss = HtmlFormatter().get_style_defs('.codehilite')
    for cssfile in glob.iglob(os.path.join(config.styledir, '*.css')):
        allcss = allcss + codecs.open(cssfile, 'r', 'utf-8').read()
    allcss = allcss.replace('{{styleurl}}', "{}style/".format(config.blogurl))

    # minimise css
    return cssmin(allcss, wrap=1000)


def write_file(filename, content):
    """ write `content` to `filename`, utf-8 encoded.

    :param filename: filename to write to
    :param content: content to write
    """
    with codecs.open(filename, 'w', 'utf-8') as afile:
        afile.write(content)
