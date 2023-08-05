
SETUP_INFO = dict(
    name = 'infi.recipe.buildout_logging',
    version = '0.1',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'https://infinigit.infinidat.com/host/infi-recipe-buildout-logging',
    license = 'PSF',
    description = """recipe enabling debug logging to files""",
    long_description = """recipe enabing debug logging to files""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['infi.recipe.console_scripts', 'zc.buildout', 'setuptools'],
    namespace_packages = ['infi', 'infi.recipe'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = {
        'console_scripts': [],
        'gui_scripts': [],
        'zc.buildout': ['default = infi.recipe.buildout_logging:BuildoutLogging']
        }
)

if SETUP_INFO['url'] is None:
    _ = SETUP_INFO.pop('url')

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

