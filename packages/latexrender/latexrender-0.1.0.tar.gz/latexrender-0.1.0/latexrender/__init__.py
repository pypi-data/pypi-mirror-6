#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import hashlib
import logging
import os
import shutil
import subprocess
from tempfile import mkdtemp

from distutils import version
from distutils.spawn import find_executable
from flask import Flask, send_file, abort
from jinja2 import Template
from PIL import Image, ImageOps


__author__ = 'Luke Pomfrey'
__email__ = 'lpomfrey@gmail.com'
__version__ = '0.1.0'
version_info = tuple(version.LooseVersion(__version__).version)


OUTPUT_DIR = os.environ.get('LATEXRENDER_OUTPUT_DIR', '/tmp/latexrender/')
TEMPLATE = os.environ.get('LATEXRENDER_TEMPLATE')
XELATEX = os.environ.get('LATEXRENDER_XELATEX')
PDFTOPS = os.environ.get('LATEXRENDER_PDFTOPS')
USE_X_SENDFILE = os.environ.get('USE_X_SENDFILE', 'true') in (
    'true', 't', 'y', 'yes', '1', 'on')


app = Flask('latexrender')
app.config.from_object(__name__)


log = logging.getLogger(__name__)
logging.basicConfig()


class SuspiciousOperation(Exception):
    pass


class InvalidLatex(Exception):
    pass


class LatexRenderer(object):

    def __init__(self, output_dir, template=None, latex=None, pdftops=None):
        self.output_dir = os.path.abspath(output_dir)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.latex = latex or find_executable('xelatex')
        self.pdftops = pdftops or find_executable('pdftops')
        self.template = \
            template or os.path.join(os.path.dirname(__file__), 'template.tex')
        assert self.latex, 'No xelatex executable found'
        assert self.pdftops, 'No pdftops executable found'
        self.illegal_tags = [
            '\\afterassignment',
            '\\aftergroup',
            '\\errhelp',
            '\\errorstopmode',
            '\\every',
            '\\expandafter',
            '\\lowercase',
            '\\newhelp',
            '\\noexpand',
            '\\nonstopmode',
            '\\read',
            '\\relax',
            '\\scrollmode',
            '\\special'
            '\\uppercase',
            '\\write',
            '\\batchmode',
            '^^',
            'catcode',
            'command',
            'csname',
            'def',
            'include',
            'input',
            'loop',
            'name',
            'open',
            'output',
            'repeat',
            'toks',
        ]

    def render_template(self, latex, **kwargs):
        with open(self.template, 'r') as tmpl:
            template = Template(tmpl.read())
        return template.render(latex=latex, **kwargs)

    def render_image(self, working_dir, basename, latex, img_filename):
        tex_filename = os.path.join(working_dir, '{0}.tex'.format(basename))
        pdf_filename = os.path.join(working_dir, '{0}.pdf'.format(basename))
        ps_filename = os.path.join(working_dir, '{0}.ps'.format(basename))
        with open(tex_filename, 'w') as tex_file:
            tex_file.write(latex)
        latex_args = [
            self.latex,
            '-interaction=nonstopmode',
            '-output-directory={0}'.format(working_dir),
            tex_filename
        ]
        try:
            subprocess.check_call(latex_args)
        except subprocess.CalledProcessError:
            raise InvalidLatex('Error running latex command')
        pdftops_args = [
            self.pdftops,
            pdf_filename,
            ps_filename
        ]
        subprocess.check_call(pdftops_args)
        img = Image.open(ps_filename)
        img = ImageOps.crop(img, border=1)
        if not os.path.exists(os.path.dirname(img_filename)):
            os.makedirs(os.path.dirname(img_filename))
        with open(img_filename, 'w+') as img_file:
            img.save(img_file, 'PNG')
        return img_filename

    def render(self, b64latex):
        basename = hashlib.md5(b64latex).hexdigest()
        img_filename = os.path.join(
            self.output_dir, '{0}.png'.format(basename)
        )
        if os.path.exists(img_filename):
            return img_filename
        working_dir = mkdtemp(prefix='latexrenderwd')
        latex = base64.b64decode(b64latex)
        if any(tag in latex for tag in self.illegal_tags):
            raise SuspiciousOperation('Illegal tag found')
        latex = self.render_template(latex)
        self.render_image(working_dir, basename, latex, img_filename)
        shutil.rmtree(working_dir)
        return img_filename


app.renderer = LatexRenderer(
    output_dir=app.config['OUTPUT_DIR'],
    template=app.config['TEMPLATE'],
    latex=app.config['XELATEX'],
    pdftops=app.config['PDFTOPS'],
)


@app.route('/<b64latex>.png')
@app.route('/<b64latex>/')
def latexrender(b64latex=''):
    try:
        return send_file(app.renderer.render(b64latex))
    except (SuspiciousOperation, InvalidLatex):
        return abort(400)
    except (Exception, EnvironmentError) as e:
        log.exception(e)
        return abort(500)


if __name__ == '__main__':
    app.run()
