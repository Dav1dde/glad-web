import os
import tempfile
import zipfile
from collections import namedtuple
from itertools import izip_longest, chain
from urllib import urlencode

from flask import Blueprint, request, render_template, g, url_for, redirect, flash, current_app

from glad.util import parse_version
from gladweb.util import write_dir_to_zipfile

Version = namedtuple('Version', ['major', 'minor'])


index = Blueprint('index', __name__)


@index.route('/', methods=['GET'])
def landing():
    return render_template(
        'index.html', **g.metadata.as_dict()
    )


def glad_generate():
    # Form data
    apis = dict(api.split('=') for api in request.form.getlist('api'))
    profiles = dict(p.split('=') for p in request.form.getlist('profile'))
    language = request.form.get('language')
    extensions = request.form.getlist('extensions')
    options = request.form.getlist('option')

    # Other
    # the suffix is required because mkdtemp sometimes creates directories with an
    # underscore at the end, we later use werkzeug.utils.secure_filename on that directory,
    # this function happens to strip underscores...
    out_path = tempfile.mkdtemp(dir=current_app.config['TEMP'], suffix='glad')
    os.chmod(out_path, 0o750)

    for api, version in apis.items():
        if version.lower().strip() == 'none':
            continue

        version = parse_version(version)
        profile = profiles.get(api)

        specification = g.metadata.get_specification_for_api(api)

        # TODO extension filtering (GLES and GL)
        feature_set = specification.select(api, version, profile, extensions)

        Generator = g.metadata.get_generator_for_language(language)
        config = Generator.Config()
        # TODO: more than just boolean configs
        for option in options:
            config.set(option, True)
        config.validate()

        generator = Generator(out_path)
        generator.generate(specification, feature_set, config)

    with zipfile.ZipFile(os.path.join(out_path, 'glad.zip'), mode='w') as zipf:
        write_dir_to_zipfile(out_path, zipf, exclude=['glad.zip'])

    serialized = urlencode(list(chain.from_iterable(
        izip_longest('', x[1], fillvalue=x[0]) for x in request.form.lists())
    ))
    # Poor mans database
    serialized_path = os.path.join(out_path, '.serialized')
    with open(serialized_path, 'w') as fobj:
        fobj.write(serialized)

    name = os.path.split(out_path)[1]
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
