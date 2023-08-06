
SETUP_INFO = dict(
    name = 'infi.git_mirror',
    version = '0.0.8',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'https://infinigit.infinidat.com/it/git_mirror',
    license = 'PSF',
    description = """A simple console script for mirroring git repositories between two remotes.""",
    long_description = """A simple console script for mirroring git repositories between two remotes.""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['infi.execute',
'infi.pyutils',
'setuptools'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['mirror_git_repository = infi.git_mirror.scripts:mirror_git_repository'],
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

