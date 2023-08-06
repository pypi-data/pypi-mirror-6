from distutils.core import setup

def fread(path):
  with open(path) as f:
    return f.read()

def version():
  return fread('VERSION').strip()

setup(
  name              = 'hg-request-pull',
  version           = version(),
  author            = 'Roman Neuhauser',
  author_email      = 'neuhauser@sigpipe.cz',
  url               = 'https://bitbucket.org/roman.neuhauser/hg-request-pull',
  description       = 'generate a summary of pending changes',
  long_description  = fread('README.txt'),
  classifiers       = fread('pypi/classification').splitlines(),
  keywords          = 'git hg mercurial pull-request',
  license           = 'GPLv3',
  packages          = [''],
  package_dir       = {'hgext': '.'},
  py_modules        = ['hgext.request-pull'],
)
