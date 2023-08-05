
SETUP_INFO = dict(
    name = 'dowser',
    version = '0.2',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'https://github.com/Infinidat/dowser',
    license = 'PSF',
    description = """Debugging Python’s Memory Usage with Dowser""",
    long_description = """Debugging Python’s Memory Usage with Dowser""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['CherryPy',
'infi.recipe.console_scripts',
'Pillow',
'setuptools'],
    namespace_packages = [],

    package_dir = {'': 'src'},
    package_data = {'': ['tree.html', 'trace.html', 'main.css', 'graphs.html']},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['dowser = dowser:main'],
        gui_scripts = [],
        ),
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

