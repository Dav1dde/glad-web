from collections import OrderedDict, namedtuple
import glad.lang.c
import glad.lang.d
import glad.lang.volt
import glad.spec
import time
import json


Language = namedtuple('Language', ['id', 'name'])
LANGUAGES = [
    Language('c', 'C/C++'),
    Language('d', 'D'),
    Language('volt', 'Volt')
]

GENERATORS = {
    'c': glad.lang.c.CGenerator,
    'd': glad.lang.d.DGenerator,
    'volt': glad.lang.volt.VoltGenerator
}

Specification = namedtuple('Specification', ['id', 'name'])
SPECIFICATIONS = [
    Specification('gl', 'OpenGL'),
    Specification('egl', 'EGL'),
    Specification('glx', 'GLX'),
    Specification('wgl', 'WGL')
]

Profile = namedtuple('Profile', ['id', 'name', 'specification'])
PROFILES = [
    Profile('compatibility', 'Compatibility', 'gl'), Profile('core', 'Core', 'gl')
]

Api = namedtuple('Api', ['id', 'name', 'specification', 'versions', 'default'])
Version = namedtuple('Version', ['id', 'name', 'tuple'])
#  APIS = [
#      Api('gl', 'gl', 'gl', [Version('1.0', 'Version 1.0'), Version('none', 'None')], '1.0'),
#      Api('gles1', 'gles1', 'gl', [Version('1.0', 'Version 1.0'), Version('none', 'None')], 'none'),
#      Api('gles2', 'gles2', 'gl', [Version('1.0', 'Version 1.0'), Version('none', 'None')], 'none'),
#      Api('egl', 'egl', 'egl', [Version('1.0', 'Version 1.0'), Version('none', 'None')], '1.0'),
#      Api('glx', 'glx', 'glx', [Version('1.0', 'Version 1.0'), Version('none', 'None')], '1.0'),
#      Api('wgl', 'wgl', 'wgl', [Version('1.0', 'Version 1.0'), Version('none', 'None')], '1.0')
#  ]

Extension = namedtuple('Extension', ['id', 'name', 'specification', 'api'])
#  EXTENSIONS = [
#      Extension('GL_EXT_TEST_GLES1', 'GL_EXT_TEST_GLES1', 'gl', 'gles1'),
#      Extension('GL_EXT_TEST_GLES2', 'GL_EXT_TEST_GLES2', 'gl', 'gles2'),
#      Extension('GL_EXT_TEST_GL', 'GL_EXT_TEST_GL', 'gl', 'gl'),
#      Extension('GLX_EXT_TEST', 'GLX_EXT_TEST', 'glx', 'glx')
#  ]

Option = namedtuple('Option', ['id', 'language', 'name', 'description'])


class Metadata(object):
    def __init__(self, cache):
        self.cache = cache

        self.languages = LANGUAGES[:]
        self.specifications = SPECIFICATIONS[:]
        self.profiles = PROFILES[:]

        self.apis = list()
        self.extensions = list()

        self.options = list()

        self.created = None

        if not self.cache.exists('metadata.json'):
            self.refresh_metadata()
        else:
            self.read_metadata()

    def read_metadata(self):
        with self.cache.open('metadata.json') as f:
            data = json.load(f)

        self.languages = [Language(*lang) for lang in data['languages']]
        self.specifications = [Specification(*spec) for spec in data['specifications']]
        self.profiles = [Profile(*profile) for profile in data['profiles']]
        self.apis = list()
        for api in data['apis']:
            versions = [Version(*v) for v in api[3]]
            self.apis.append(Api(api[0], api[1], api[2], versions, api[4]))
        self.extensions = [Extension(*ext) for ext in data['extensions']]
        self.options = [Option(*opt) for opt in data['options']]
        self.created = data['created']

    def refresh_metadata(self):
        self.apis = list()
        self.extensions = list()

        for specification in self.specifications:
            with self.cache.open_specification(specification.id) as f:
                cls = glad.spec.SPECIFICATIONS[specification.id]
                data = cls.fromstring(f.read())

            for api, versions in data.features.items():
                v = list()
                for version in versions:
                    id_ = '.'.join(map(str, version))
                    v.append(Version(id_, 'Version {0}'.format(id_), version))
                v.append(Version('none', 'None', None))

                # TODO: set default
                self.apis.append(Api(api, api, specification.id, v, 'none'))

            for api, extensions in data.extensions.items():
                for name, extension in extensions.items():
                    self.extensions.append(Extension(name, name, specification.id, api))

        self.options = list()
        for language in LANGUAGES:
            Generator = GENERATORS[language.id]

            config = Generator.Config()

            # TODO config options other than boolean
            for name, option in config.items():
                self.options.append(Option(
                    name, language.id, name.lower().replace('_', ' '), option.description
                ))

        self.created = time.time()

        try:
            self.cache.remove('metadata.json')
        except OSError:
            pass

        with self.cache.open('metadata.json', 'w') as f:
            json.dump(self.as_dict(), f)

    def as_dict(self):
        return {
            'languages': self.languages,
            'specifications': self.specifications,
            'profiles': self.profiles,
            'apis': self.apis,
            'extensions': self.extensions,
            'options': self.options,
            'created': self.created
        }
