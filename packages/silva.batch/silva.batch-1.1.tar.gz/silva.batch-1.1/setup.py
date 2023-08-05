from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='silva.batch',
      version=version,
      description="Batch integration for Silva CMS",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        ],
      keywords='batch silva pagination',
      author='Antonin Amand',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/silva.batch',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['silva'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zeam.utils.batch',
          'silva.core.views',
          'grokcore.component',
          ],
      )
