import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.md')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'requests>=2.0'
    ]

setup(name='pyramid_vgid_oauth2',
      version='1.0.2',
      description='pyramid_vgid_oauth2',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Tarzan',
      author_email='hoc3010@gmail.com',
      url='http://gitlab.vnpid.com/vgid/pyramid_vgid_oauth2',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='pyramid_vgid_oauth2',
      install_requires=requires,
      )
