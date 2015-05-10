from collections import namedtuple
import importlib
import os
import io
import shutil
import tempfile
import zipfile
from flask import Blueprint, request, render_template, g, url_for, redirect, flash, send_file, current_app
import glad.lang.c.generator
from glad.spec import SPECS


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
    profile = request.form.get('profile', 'core')
    apis = request.form.getlist('api')
    extensions = request.form.getlist('extensions')
    loader = request.form.get('loader') is not None

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


def write_dir_to_zipfile(path, zipf):
    for root, dirs, files in os.walk(path):
        for file_ in files:
            zipf.write(
                os.path.join(root, file_),
                os.path.relpath(os.path.join(root, file_), path)
            )


def glad_generate():
    language, specification, profile, apis, extensions, loader_enabled = validate_form()

    cls = SPECS[specification]
    spec = cls.fromstring(g.cache.open_specification(specification).read())
    if spec.NAME == 'gl':
        spec.profile = profile

    mod = importlib.import_module('glad.lang.{0}'.format(language))

    try:
        loader_cls = getattr(mod, '{0}Loader'.format(spec.NAME.upper()))
        loader = loader_cls()
        loader.disabled = not loader_enabled
    except KeyError:
        raise ValueError('API/Spec not supported')

    glad.lang.c.generator.KHRPLATFORM = g.cache.get_khrplatform()

    directory = tempfile.mkdtemp()
    with mod.Generator(directory, spec, apis, loader) as generator:
        generator.generate(extensions)

    try:
        fobj = io.BytesIO()
        zipf = zipfile.ZipFile(fobj, mode='w')
        write_dir_to_zipfile(directory, zipf)
        zipf.close()
    finally:
        shutil.rmtree(directory)

    fobj.seek(0, io.SEEK_SET)
    return fobj

@index.route('/generate', methods=['POST'])
def generate():
    try:
        fobj = glad_generate()
    except Exception, e:
        current_app.logger.exception(e)
        current_app.logger.error(request.form)
        flash(e.message, category='error')
        return redirect(url_for('index.landing'))

    return send_file(
        fobj, mimetype='application/octet-stream',
        as_attachment=True, attachment_filename='glad-generated.zip'
    )
