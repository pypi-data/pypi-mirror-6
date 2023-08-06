from os.path import abspath, dirname, join

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys


class ToxTestCommand(TestCommand):
    """Test command which runs tox under the hood."""

    def finalize_options(self):
        """Add options to the test runner (tox)."""
        TestCommand.finalize_options(self)
        self.test_args = ['--recreate']
        self.test_suite = True

    def run_tests(self):
        """Invoke the test runner (tox)."""
        #import here, cause outside the eggs aren't loaded
        import detox.main
        errno = detox.main.main(self.test_args)
        sys.exit(errno)

long_description = []

for text_file in ['README.rst', 'CHANGES.rst']:
    with open(join(dirname(abspath(__file__)), text_file), 'r') as f:
        long_description.append(f.read())

setup(
    name='pltk',
    description='Paylogic Toolkit',
    long_description='\n'.join(long_description),
    version='0.3',
    author='Paylogic International',
    author_email='developers@paylogic.com',
    license='MIT',
    install_requires=['redis',
                      'PyContracts',
                      'pymongo',
                      'flask',
                      'werkzeug',
                      'pyContracts',
                      'speaklater',
                      ],
    dependency_links=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    tests_require=['detox'],
    cmdclass={'test': ToxTestCommand},
    package_data={'pltk': ['sphinx_utils/paylogic_theme/*.conf',
                           'sphinx_utils/paylogic_theme/static/*.css'
                           ],
                  }
)
