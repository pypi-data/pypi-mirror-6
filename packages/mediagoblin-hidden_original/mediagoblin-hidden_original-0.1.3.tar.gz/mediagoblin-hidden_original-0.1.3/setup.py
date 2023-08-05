#!/usr/bin/env python
import pytest
from setuptools import setup, Command

class TestCommand(Command):
    """Runs the test suite."""
    description = """Runs the test suite."""
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import pytest
        pytest.main('./tests')

__VERSION__="0.1.3"
setup(
    name='mediagoblin-hidden_original',
    version=__VERSION__,
    description='Hide original files, show only downsized ones.',
    author='Kevin Brubeck Unhammer',
    author_email='unhammer@fsfe.org',
    url='https://gitorious.org/mediagoblin-stock/mediagoblin-hidden_original',
    download_url='https://gitorious.org/mediagoblin-stock/mediagoblin-hidden_original/archive/mediagoblin-hidden_original-v'+__VERSION__+'.tar.gz',
    packages=['mediagoblin_hidden_original'],
    include_package_data=True,
    license=(b'License :: OSI Approved :: GNU Affero General Public License '
             b'v3 or later (AGPLv3+)'),
    cmdclass={'test': TestCommand},
)
