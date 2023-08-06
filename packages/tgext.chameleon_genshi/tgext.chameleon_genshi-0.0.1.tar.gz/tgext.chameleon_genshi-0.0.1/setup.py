from setuptools import setup, find_packages
import os

version = '0.0.1'

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''

setup(name='tgext.chameleon_genshi',
      version=version,
      description="Chameleon Genshi rendering engine for TurboGears2",
      long_description=README,
      classifiers=[
        "Environment :: Web Environment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: TurboGears"
        ],
      keywords='turbogears2.extension',
      author='Alessandro Molina',
      author_email='alessandro.molina@axant.it',
      url='https://github.com/TurboGears/tgext.chameleon_genshi',
      license='MIT',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['tgext'],
      zip_safe=False,
      install_requires=[
        "TurboGears2 >= 2.3.2",
        'Chameleon < 2.0a'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
