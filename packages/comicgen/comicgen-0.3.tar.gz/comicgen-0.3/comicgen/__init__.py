import glob
import os
import shutil
import subprocess
from datetime import datetime
from tempfile import mkdtemp
from uuid import uuid1

import cli.app
from jinja2 import Environment, PackageLoader


class TempDir(object):

    def __init__(self, prefix):
        self.prefix = prefix

    def __enter__(self):
        self.path = mkdtemp(prefix='comicgen_')
        return self

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.path)

    def path_to(self, name):
        return os.path.join(self.path, name)

    def make_file(self, name, content):
        with open(self.path_to(name), 'w') as fh:
            fh.write(content)

    def copy_file(self, src, dist, abs_src_path=False, abs_dist_path=False):
        if not abs_src_path:
            src = self.path_to(src)
        if not abs_dist_path:
            dist = self.path_to(dist)
        shutil.copyfile(src, dist)

    def make_dir(self, name):
        os.makedirs(self.path_to(name))


def generate(params):
    with TempDir('comicgen_') as temp_dir:
        jinja2_env = Environment(loader=PackageLoader('comicgen', 'templates'))
        uuid = str(uuid1())

        image_paths = glob.glob(os.path.join(params.image_dir, '*.jpg'))
        indexes = sorted([os.path.basename(name).replace('.jpg', '') for name in image_paths])

        template_params = dict(
            indexes=indexes,
            uuid=uuid,
            title=params.title,
            author=params.author,
            publisher=params.publisher,
            publication=params.publication)

        ncx_template = jinja2_env.get_template('ncx.jinja2')
        temp_dir.make_file('%s.ncx' % params.title, ncx_template.render(**template_params))

        opf_template = jinja2_env.get_template('opf.jinja2')
        temp_dir.make_file('%s.opf' % params.title, opf_template.render(**template_params))

        page_template = jinja2_env.get_template('page.jinja2')
        for i in indexes:
            temp_dir.make_file('%s.html' % i, page_template.render(i=i))

        temp_dir.make_dir('images')
        for image_path in image_paths:
            temp_dir.copy_file(image_path, 'images/' + os.path.basename(image_path), abs_src_path=True)

        temp_dir.make_file('cover.html', page_template.render(i='cover'))
        temp_dir.copy_file('images/%s.jpg' % indexes[0], 'images/cover.jpg')

        subprocess.call("%(kindlegen)s '%(opf_path)s'" % dict(
            kindlegen=params.kindlegen,
            opf_path=temp_dir.path_to('%s.opf' % params.title)), shell=True)

        mobifile = '%s.mobi' % params.title
        temp_dir.copy_file(mobifile, os.path.join(params.output, mobifile), abs_dist_path=True)


@cli.app.CommandLineApp
def comicgen(app):
    generate(app.params)


@cli.app.CommandLineApp
def comicgen_volumes(app):
    volume_paths = glob.glob(os.path.join(app.params.volume_dir, '*'))
    for volume_path in volume_paths:
        volume = int(os.path.basename(volume_path))
        app.params.image_dir = volume_path
        app.params.title = app.params.title_template % dict(volume=volume)
        generate(app.params)


def comicgen_script():
    comicgen.add_param('image_dir', help='A path to the dir containing target images.', default=None, type=str)

    comicgen.add_param('-t', '--title', help='A title for the ebook.', default='comic', type=str)
    comicgen.add_param('-a', '--author', help='An author for the ebook.', default='author', type=str)
    comicgen.add_param('-p', '--publisher', help='A publisher for the ebook.', default='publisher', type=str)
    comicgen.add_param('-y', '--publication', help='A pablication year for the ebook.', default=datetime.now().year, type=int)

    comicgen.add_param('-k', '--kindlegen', help='A path for your kindlegen program.', default='kindlegen', type=str)
    comicgen.add_param('-o', '--output', help='A path to store the generated ebook.', default='./', type=str)
    comicgen.run()


def comicgen_volumes_script():
    comicgen_volumes.add_param('volume_dir', help='A path to the dir containing target volumes.', default=None, type=str)

    comicgen_volumes.add_param('-t', '--title-template', help='A template string for the ebook title. [ex. Title Vol.%(volume)i]', default='Comic Vol.%(volume)i', type=str)
    comicgen_volumes.add_param('-a', '--author', help='An author for the ebook.', default='author', type=str)
    comicgen_volumes.add_param('-p', '--publisher', help='A publisher for the ebook.', default='publisher', type=str)
    comicgen_volumes.add_param('-y', '--publication', help='A pablication year for the ebook.', default=datetime.now().year, type=int)

    comicgen_volumes.add_param('-k', '--kindlegen', help='A path for your kindlegen program.', default=None, type=str)
    comicgen_volumes.add_param('-o', '--output', help='A path to store the generated ebook.', default='./', type=str)
    comicgen_volumes.run()
