from setuptools import setup, find_packages
import os

version = '0.1.0'

setup(name='rt.zestreleaser.pyflakes',
      version=version,
      description="Plugin for zest.releaser to allow check your Python code "
                  "with Pyflakes before making a release",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.rst")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        'Programming Language :: Python',
        'Environment :: Console',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: System :: Archiving :: Packaging',
        'Topic :: System :: Installation/Setup',
        'Topic :: Utilities',
        ],
      keywords='releaser zest.releaser egg pyflakes',
      author='RedTurtle Technology',
      author_email='keul@redturtle.it',
      url='https://github.com/RedTurtle/rt.zestreleaser.pyflakes',
      license='GPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['rt', 'rt.zestreleaser'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zest.releaser',
          'pyflakes',
      ],
      test_suite="nose.collector",
      tests_require=['nose', 'mock'],
      setup_requires=['nose>=1.0',],
      entry_points={
        'zest.releaser.prereleaser.after':
            ['pyflakes=rt.zestreleaser.pyflakes.pyflakes_checker:check',]},
      )
