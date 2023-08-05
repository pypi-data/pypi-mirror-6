from setuptools import setup, find_packages
import os

version = '1.2.2'

tests_require = [
    'Products.Silva [test]',
    ]

setup(name='silva.security.logging',
      version=version,
      description="Log all actions inside Silva CMS in a file or SQL table",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='silva cms zope security',
      author='Infrae',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/silva.security.logging',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['silva', 'silva.security'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'five.grok',
        'setuptools',
        'silva.core.conf',
        'silva.core.interfaces',
        'silva.core.services',
        'silva.core.views',
        'zeam.form.silva',
        'zope.component',
        'zope.container',
        'zope.interface',
        'zope.intid',
        'zope.keyreference',
        'zope.lifecycleevent',
        'zope.schema',
        ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
