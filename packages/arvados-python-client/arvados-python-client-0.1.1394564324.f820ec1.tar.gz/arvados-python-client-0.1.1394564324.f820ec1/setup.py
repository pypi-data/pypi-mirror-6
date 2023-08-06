from setuptools import setup
import subprocess

minor_version = '1394564324.f820ec1'

setup(name='arvados-python-client',
      version='0.1.' + minor_version,
      description='Arvados client library',
      author='Arvados',
      author_email='info@arvados.org',
      url="https://arvados.org",
      download_url="https://github.com/curoverse/arvados.git",
      license='Apache 2.0',
      packages=['arvados'],
      scripts=[
        'bin/arv-get',
        'bin/arv-put',
        'bin/arv-mount',
        'bin/arv-ls',
        'bin/arv-normalize',
        ],
      install_requires=[
        'python-gflags',
        'google-api-python-client',
        'httplib2',
        'urllib3',
	'llfuse'
        ],
      zip_safe=False)
