try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

packages = ['senticnet']
requires = []

setup(name='senticnet',
      version='0.3.3',
      description='Access Senticnet API using Python',
      long_description=open('README.md').read(),
      author=u'Yuri Malheiros',
      author_email='contato@yurimalheiros.com',
      url='https://github.com/yurimalheiros/senticnetapi',
      packages=packages,
      package_data={'': ['LICENSE', 'README.md'], 'senticnet': []},
      package_dir={'senticnet': 'senticnet'},
      include_package_data=True,
      license=open('LICENSE').read(),
      zip_safe=False,
      install_requires=['rdflib==3.2.1',],
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries'],
)
