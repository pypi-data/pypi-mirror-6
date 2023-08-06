import sys
from distutils.core import setup, Command

# This is a hack in order to get the package name to be different when
#  building an RPM file. When 'setup.py bdist_rpm' is called, it invokes
#  setup.py twice more, with these command lines:
# ['setup.py', 'build']
# ['setup.py', 'install', '-O1', '--root=<path>', '--record=INSTALLED_FILES']
# It's only on the original call (when bdist_rpm is in sys.argv) that
#  I adjust the package name. With Python 2.7, that's enough. I'm not
#  sure about 3.x.

name = 'header-detail-footer'
if 'bdist_rpm' in sys.argv:
    name = 'python-' + name

# run our tests
class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys, subprocess
        errno = subprocess.call([sys.executable, 'header_detail_footer.py'])
        raise SystemExit(errno)


setup(name=name,
      version='2.3',
      url='https://bitbucket.org/ericvsmith/header-detail-footer',
      author='Eric V. Smith',
      author_email='eric@trueblade.com',
      description='Parse input streams with headers and footers.',
      long_description=open('README.txt').read() + '\n' + open('CHANGES.txt').read(),
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Apache Software License',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3',
                   ],
      license='Apache License Version 2.0',
      py_modules=['header_detail_footer'],

      cmdclass = {'test': PyTest},
      )
