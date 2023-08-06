import sys
from pprint import pprint

from paver.easy import task, needs, path, sh, cmdopts, options
from paver.setuputils import setup, find_package_data

import version
# Add package directory to Python path. This enables the use of
# `electromagnet_controller` functions for discovering, e.g., the path to the
# Arduino firmware sketch source files.
sys.path.append(path('.').abspath())
import electromagnet_controller

electromagnet_controller_files = find_package_data(
    package='electromagnet_controller', where='electromagnet_controller',
    only_in_packages=False)
pprint(electromagnet_controller_files)

setup(name='wheeler.electromagnet_controller',
      version=version.getVersion(),
      description='Arduino-based electromagnet controller firmware and Python'
      'API.',
      author='Ryan Fobel',
      author_email='ryan@fobel.net',
      url='http://microfluidics.utoronto.ca/git/firmware___electromagnet_controller.git',
      license='GPLv2',
      packages=['electromagnet_controller'],
      package_data=electromagnet_controller_files,
      install_requires=['wheeler.base_node'])


@task
def create_config():
    sketch_directory = path(electromagnet_controller.get_sketch_directory())
    sketch_directory.joinpath('Config.h.skeleton').copy(sketch_directory
                                                        .joinpath('Config.h'))


@task
@needs('create_config')
@cmdopts([('sconsflags=', 'f', 'Flags to pass to SCons.')])
def build_firmware():
    sh('scons %s' % getattr(options, 'sconsflags', ''))


@task
@needs('generate_setup', 'minilib', 'build_firmware',
       'setuptools.command.sdist')
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass
