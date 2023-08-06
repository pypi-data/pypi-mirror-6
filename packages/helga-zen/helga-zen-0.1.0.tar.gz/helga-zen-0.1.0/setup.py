from setuptools import setup, find_packages


version = '0.1.0'


setup(name="helga-zen",
      version=version,
      description=('The Zen of Python as a helga plugin'),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Topic :: Communications :: Chat :: Internet Relay Chat',
          'Framework :: Twisted',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='helga zen',
      author='Shaun Duncan',
      author_email='shaun.duncan@gmail.com',
      url='https://github.com/shaunduncan/helga-zen',
      license='GPLv3',
      packages=find_packages(),
      py_modules=['helga_zen'],
      entry_points = dict(
          helga_plugins=[
              'zen = helga_zen:zen'
          ],
      ),
)
