import os
import tempfile
import zipfile
from collections import namedtuple
from itertools import izip_longest, chain
from urllib import urlencode

from flask import Blueprint, request, render_template, g, url_for, redirect, flash, current_app

import glad.spec
from gladweb.util import write_dir_to_zipfile

Version = namedtuple('Version', ['major', 'minor'])


index = Blueprint('index', __name__)


@index.route('/', methods=['GET'])
def landing():
    return render_template(
        'index.html', **g.metadata.as_dict()
    )


def validate_form():
    language = request.form.get('language')
    apis = request.form.getlist('api')
    extensions = request.form.getlist('extensions')

    if language not in (l.id for l in g.metadata.languages):
        raise ValueError('Invalid language "{0}"'.format(language))

    if specification not in (s.id for s in g.metadata.specifications):
        raise ValueError('Invalid specification "{0}"'.format(specification))

    if profile not in (p.id for p in g.metadata.profiles):
        raise ValueError('Invalid profile "{0}"'.format(profile))

    apis_parsed = dict()
    for api in apis:
        name, version = api.split('=')
        if version == 'none':
            continue
        apis_parsed[name] = Version(*map(int, version.split('.')))

    if len(apis_parsed) == 0:
        raise ValueError(
            'No API for specification selected'.format(specification)
        )

    return language, specification, profile, apis_parsed, extensions, loader


def glad_generate():
    language, specification, profile, apis, extensions, loader_enabled = validate_form()

    g.metadata.get_specification_for_api()

    # the suffix is required because mkdtemp sometimes creates directories with an
    # underscore at the end, we later use werkzeug.utils.secure_filename on that directory,
    # this function happens to strip underscores...
    directory = tempfile.mkdtemp(dir=current_app.config['TEMP'], suffix='glad')
    os.chmod(directory, 0o750)
    with generator_cls(directory, spec, apis, extensions, loader) as generator:
        generator.generate()

    zip_path = os.path.join(directory, 'glad.zip')
    with open(zip_path, 'w') as fobj:
        zipf = zipfile.ZipFile(fobj, mode='w')
        write_dir_to_zipfile(directory, zipf, exclude=['glad.zip'])
        zipf.close()

    serialized = urlencode(list(chain.from_iterable(
        izip_longest('', x[1], fillvalue=x[0]) for x in request.form.lists())
    ))
    serialized_path = os.path.join(directory, '.serialized')
    with open(serialized_path, 'w') as fobj:
        fobj.write(serialized)

    name = os.path.split(directory)[1]
    if current_app.config['FREEZE']:
        current_app.freezer.freeze(name)
    return url_for('generated.autoindex', root=name)


@index.route('/generate', methods=['POST'])
def generate():
    try:
        url = glad_generate()
    except Exception, e:
        current_app.logger.exception(e)
        current_app.logger.error(request.form)
        flash(e.message, category='error')
        return redirect(url_for('index.landing'))

    return redirect(url)
