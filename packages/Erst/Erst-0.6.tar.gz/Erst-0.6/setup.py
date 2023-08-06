from setuptools import setup, find_packages

setup(
    name = 'Erst',
    version = '0.6',
    packages = find_packages(),
    scripts = ['erst.py'],

    install_requires = ['mercurial', 'fusepy>=2.0.2'],

    package_data = {
        '': ['README']
    },

    author = 'Eric Estabrooks',
    author_email = 'estabroo@gmail.com',
    description = 'An automatic versioning fuse filesystem',
    license = 'Apache License 2.0 - http://www.apache.org/licenses/LICENSE-2.0.html',
    keywords = "erst mercurial revision versioning automatic",
)
