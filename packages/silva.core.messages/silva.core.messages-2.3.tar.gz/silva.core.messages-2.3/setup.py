from setuptools import setup, find_packages
import os

version = '2.3'

tests_require = [
    'Products.Silva [test]',
    'zope.publisher',
    'zope.component',]

setup(name='silva.core.messages',
      version=version,
      description="User feedback mechanism for Silva CMS",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        ],
      keywords='silva core messages',
      author='Infrae',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/silva.core.messages',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva', 'silva.core'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'five.grok',
        'silva.core.cache',
        'zope.interface',
      ],
      tests_require=tests_require,
      extras_require={'test': tests_require},
      )
