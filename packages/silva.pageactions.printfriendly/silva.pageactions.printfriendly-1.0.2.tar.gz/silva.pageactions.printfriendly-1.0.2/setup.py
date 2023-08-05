from setuptools import setup, find_packages
import os

version = '1.0.2'

setup(name='silva.pageactions.printfriendly',
      version=version,
      description="Display a simple printable version of the content in Silva CMS",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='silva pageactions print',
      author='Infrae',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/silva.pageactions.printfriendly',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['silva', 'silva.pageactions'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'silva.core.views  > 2.0.999, < 2.1.999',
          'silva.pageactions.base',
          'five.grok',
          'megrok.chameleon',
          ],
      )
