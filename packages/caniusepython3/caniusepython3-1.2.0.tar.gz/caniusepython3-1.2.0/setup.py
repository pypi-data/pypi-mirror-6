from setuptools import setup


# Installed name used for various commands (both script and setuptools).
command_name = 'caniusepython3'  # 'icanhazpython3'

with open('README.md') as file:
    # Try my best to have at least the intro in Markdown/reST.
    long_description = file.read().partition('<!-- END long_description -->')[0]

setup(name='caniusepython3',
      version='1.2.0',
      description='Determine what projects are blocking you from porting to Python 3',
      long_description=long_description,
      author='Brett Cannon',
      author_email='brett@python.org',
      url='https://github.com/brettcannon/caniusepython3',
      packages=['caniusepython3', 'caniusepython3.test'],
      include_package_data=True,
      install_requires=['distlib', 'setuptools', 'pip',  # Input flexibility
                        'argparse', 'futures',  # Functionality
                        'mock'],  # Testing
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
      ],
      entry_points={
          'console_scripts': [
              '{0} = caniusepython3.__main__:main'.format(command_name),
          ],
          'distutils.commands': [
              '{0} = caniusepython3.command:Command'.format(command_name),
          ],
      },
      zip_safe=True,
)
