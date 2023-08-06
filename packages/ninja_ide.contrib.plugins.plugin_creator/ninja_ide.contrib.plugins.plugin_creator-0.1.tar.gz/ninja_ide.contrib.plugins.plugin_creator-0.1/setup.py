from setuptools import setup, find_packages

setup(name='ninja_ide.contrib.plugins.plugin_creator',
      version='0.1',
      keywords="ninja_ide plugin",
      url="www.ninja-ide.org",
      author='Horacio Duran',
      author_email='perrito@ninja-ide.org',
      maintainer='Horacio Duran',
      maintainer_email='perrito@ninja-ide.org',
      namespace_packages=['ninja_ide', 'ninja_ide.contrib',
                          'ninja_ide.contrib.plugins'],
      packages=find_packages(),
      )