from setuptools import setup, find_packages
import os

version = '1.0.2'

setup(name='silva.pageactions.mailpdf',
      version=version,
      description="Send the current by mail as a PDF.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='silva pageactions mail pdf',
      author='Infrae',
      author_email='info@infrae.com',
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['silva', 'silva.pageactions'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'five.grok',
        'megrok.chameleon',
        'silva.core.views',
        'silva.pageactions.base',
        'silva.pageactions.pdf',
        'silva.captcha',
        ],
      )
