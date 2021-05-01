import json
import os
import sys
import tempfile
import zipfile
from collections import namedtuple
from flask import Blueprint, request, render_template, g, url_for, redirect, flash, current_app

import glad.lang.c.generator
from glad.spec import SPECS
from gladweb.views.exception import InvalidUserInput

if sys.version_info >= (3, 0):
    from itertools import zip_longest, chain
    from urllib.parse import urlencode
else:
    from itertools import izip_longest as zip_longest, chain
    from urllib import urlencode

Version = namedtuple('Version', ['major', 'minor'])


index = Blueprint('index', __name__)


@index.route('/', methods=['GET'])
def landing():
    return render_template(
        'index.html', **g.metadata.as_dict()
    )


def validate_form():
    language = request.form.get('language')
    specification = request.form.get('specification')
    profile = request.form.get('profile', 'compatibility')
    apis = request.form.getlist('api')
    extensions = request.form.getlist('extensions')
    loader = request.form.get('loader') is not None
    omitkhr = request.form.get('omitkhr') is not None
    local_files = request.form.get('localfiles') is not None

    messages = list()

    if language not in (l.id for l in g.metadata.languages):
        raise InvalidUserInput('Invalid language "{0}"'.format(language))

    if specification not in (s.id for s in g.metadata.specifications):
        raise InvalidUserInput('Invalid specification "{0}"'.format(specification))

    if profile not in (p.id for p in g.metadata.profiles):
        raise InvalidUserInput('Invalid profile "{0}"'.format(profile))

    apis_parsed = dict()
    for api in apis:
        name, version = api.split('=')
        if version == 'none':
            continue
        apis_parsed[name] = Version(*map(int, version.split('.')))

    if len(apis_parsed) == 0:
        raise InvalidUserInput(
            'No API for specification selected'.format(specification)
        )

    return messages, language, specification, profile, apis_parsed, extensions, loader, omitkhr, local_files


def write_dir_to_zipfile(path, zipf, exclude=None):
    if exclude is None:
        exclude = []

    for root, dirs, files in os.walk(path):
        for file_ in files:
            if file_ in exclude:
                continue

            zipf.write(
                os.path.join(root, file_),
                os.path.relpath(os.path.join(root, file_), path)
            )


def glad_generate():
    # this is really getting ugly, where did my code quality standards go?
    messages, language, specification, profile, apis, extensions, loader_enabled, omitkhr, local_files = validate_form()

    cls = SPECS[specification]
    spec = cls.fromstring(g.cache.open_specification(specification).read())
    if spec.NAME == 'gl':
        spec.profile = profile

    generator_cls, loader_cls = glad.lang.get_generator(
        language, spec.NAME.lower()
    )

    if loader_cls is None:
        raise InvalidUserInput('API/Spec not yet supported')

    loader = loader_cls(apis)
    loader.disabled = not loader_enabled
    loader.local_files = local_files

    glad.lang.c.generator.KHRPLATFORM = 'file:' + g.cache.get_khrplatform()

    # the suffix is required because mkdtemp sometimes creates directories with an
    # underscore at the end, we later use werkzeug.utils.secure_filename on that directory,
    # this function happens to strip underscores...
    directory = tempfile.mkdtemp(dir=current_app.config['TEMP'], suffix='glad')
    os.chmod(directory, 0o750)
    with generator_cls(directory, spec, apis, extensions, loader, local_files=local_files, omit_khrplatform=omitkhr) as generator:
        generator.generate()

    zip_path = os.path.join(directory, 'glad.zip')
    with open(zip_path, 'wb') as fobj:
        zipf = zipfile.ZipFile(fobj, mode='w')
        write_dir_to_zipfile(directory, zipf, exclude=['glad.zip'])
        zipf.close()

    serialized = urlencode(list(chain.from_iterable(
        zip_longest('', x[1], fillvalue=x[0]) for x in request.form.lists())
    ))
    serialized_path = os.path.join(directory, '.serialized')
    with open(serialized_path, 'w') as fobj:
        json.dump({'params': serialized, 'messages': messages}, fobj)

    name = os.path.split(directory)[1]
    if current_app.config['FREEZE']:
        current_app.freezer.freeze(name)
    return url_for('generated.autoindex', root=name)


@index.route('/generate', methods=['POST'])
def generate():
    try:
        url = glad_generate()
    except Exception as e:
        import gladweb
        if gladweb.sentry is not None:
            gladweb.sentry.captureException()

        current_app.logger.exception(e)
        current_app.logger.error(request.form)
        flash(str(e), category='error')
        return redirect(url_for('index.landing'))

    return redirect(url)
