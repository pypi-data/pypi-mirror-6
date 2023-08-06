
import os, sys

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension


if 'sdist' in sys.argv and 'upload' in sys.argv:
    import commands
    finder = "/usr/bin/find %s \( -name \*.pyc -or -name .DS_Store \) -delete"
    theplace = os.getcwd()
    if theplace not in (".", "/"):
        print("+ Deleting crapola from %s..." % theplace)
        print("$ %s" % finder % theplace)
        commands.getstatusoutput(finder % theplace)
        print("")


VERSION = '1.7'

darwin_includes = [
    '/usr/local/include',
    '/usr/local/opt/icu4c/include']
if 'INSTANCE_INCLUDE' in os.environ: # Praxa
    darwin_includes.append(os.environ['INSTANCE_INCLUDE'])
if 'LOCAL_INCLUDE' in os.environ: # Praxa (local)
    darwin_includes.append(os.environ['LOCAL_INCLUDE'])

darwin_libs = [
    '/usr/local/lib',
    '/usr/local/opt/icu4c/lib']
if 'INSTANCE_LIB' in os.environ: # Praxa
    darwin_libs.append(os.environ['INSTANCE_LIB'])
if 'LOCAL_LIB' in os.environ: # Praxa (local)
    darwin_libs.append(os.environ['LOCAL_LIB'])

INCLUDES = {
    'darwin': list(reversed(darwin_includes)),
    'linux': [],
    'freebsd': ['/usr/local/include'],
    'win32': ['c:/icu/include'],
    'sunos5': [],
}

CFLAGS = {
    'darwin': ['-Wno-write-strings', '-DPYICU_VER="%s"' %(VERSION)],
    'linux': ['-DPYICU_VER="%s"' %(VERSION)],
    'freebsd': ['-DPYICU_VER="%s"' %(VERSION)],
    'win32': ['/Zc:wchar_t', '/EHsc', '/DPYICU_VER=\\"%s\\"' %(VERSION)],
    'sunos5': ['-DPYICU_VER="%s"' %(VERSION)],
}

# added to CFLAGS when setup is invoked with --debug
DEBUG_CFLAGS = {
    'darwin': ['-O0', '-g', '-DDEBUG'],
    'linux': ['-O0', '-g', '-DDEBUG'],
    'freebsd': ['-O0', '-g', '-DDEBUG'],
    'win32': ['/Od', '/DDEBUG'],
    'sunos5': ['-DDEBUG'],
}

LFLAGS = {
    'darwin': list(reversed(map(lambda libpth: "-L%s" % libpth, darwin_libs))),
    'linux': [],
    'freebsd': ['-L/usr/local/lib'],
    'win32': ['/LIBPATH:c:/icu/lib'],
    'sunos5': [],
}

LIBRARIES = {
    'darwin': ['icui18n', 'icuuc', 'icudata', 'icule'],
    'linux': ['icui18n', 'icuuc', 'icudata', 'icule'],
    'freebsd': ['icui18n', 'icuuc', 'icudata', 'icule'],
    'win32': ['icuin', 'icuuc', 'icudt', 'icule'],
    'sunos5': ['icui18n', 'icuuc', 'icudata', 'icule'],
}

platform = sys.platform
if platform.startswith('linux'):
    platform = 'linux'
elif platform.startswith('freebsd'):
    platform = 'freebsd'

if 'PYICU_INCLUDES' in os.environ:
    _includes = os.environ['PYICU_INCLUDES'].split(os.pathsep)
else:
    _includes = INCLUDES[platform]

if 'PYICU_CFLAGS' in os.environ:
    _cflags = os.environ['PYICU_CFLAGS'].split(os.pathsep)
else:
    _cflags = CFLAGS[platform]

if '--debug' in sys.argv:
    if 'PYICU_DEBUG_CFLAGS' in os.environ:
        _cflags += os.environ['PYICU_DEBUG_CFLAGS'].split(os.pathsep)
    else:
        _cflags += DEBUG_CFLAGS[platform]

if 'PYICU_LFLAGS' in os.environ:
    _lflags = os.environ['PYICU_LFLAGS'].split(os.pathsep)
else:
    _lflags = LFLAGS[platform]

if 'PYICU_LIBRARIES' in os.environ:
    _libraries = os.environ['PYICU_LIBRARIES'].split(os.pathsep)
else:
    _libraries = LIBRARIES[platform]


cppdir = os.listdir(os.path.join(os.curdir, 'cpp'))
cppfiles = ["cpp%s%s" % (os.path.sep, filename) for filename in cppdir if filename.endswith('.cpp')]
#cppfiles.append(os.path.join(os.curdir, '_icu.cpp'))
cppfiles.append('_icu.cpp')

setup(name="pyicu-praxa",
      description='Python extension wrapping the ICU C++ API (Praxa fork)',
      long_description=open('README.rst').read(),
      version=VERSION,
      test_suite="test",
      url='http://pyicu.osafoundation.org/',
      author='Alexander Bohn',
      author_email='fish2000@gmail.com',
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved',
                   'Operating System :: OS Independent',
                   'Programming Language :: C++',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3',
                   'Topic :: Software Development :: Localization',
                   'Topic :: Software Development :: Internationalization'],
      ext_modules=[Extension('_icu', cppfiles,
                             include_dirs=_includes,
                             extra_compile_args=_cflags,
                             extra_link_args=_lflags,
                             libraries=_libraries)],
      py_modules=['icu', 'PyICU', 'docs'])


if sys.version_info >= (3,):
    path = os.path.join('test', '2to3.note')
    if not os.path.exists(path):
        from lib2to3.main import main
        main("lib2to3.fixes", ['-w', '-n', '--no-diffs', 'test'])
        output = open(path, 'w')
        output.write('tests auto-converted by 2to3 during setup\n')
        output.close()
