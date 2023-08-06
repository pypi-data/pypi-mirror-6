from setuptools import setup, find_packages


def version():
  import os
  folder       = os.path.split(__file__)[0]
  version_file = os.path.join(folder, "duxlib/_version.py")
  env = {}
  execfile(version_file, env)
  return env['__version__']

def requirements():
  import os
  folder       = os.path.split(__file__)[0]
  requirements = os.path.join(folder, "requirements.txt")
  with open(requirements, 'r') as f:
    lines = f.readlines()
    lines = [l.strip().split("#")[0] for l in lines]
    return lines


setup(
    name         = 'duxlib',
    version      = version(),
    author       = 'Daniel Duckworth',
    author_email = 'duckworthd@gmail.com',
    description  = "Extensions to Python libraries",
    license      = 'BSD',
    keywords     = 'libraries extensions',
    url          = 'http://github.com/duckworthd/duxlib',
    packages     = find_packages(),
    classifiers  = [
      'Development Status :: 4 - Beta',
      'License :: OSI Approved :: BSD License',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
    ],

    # since duxlib is more like an amalgamation of minimodules, I'll forgo
    # actually requiring them and instead let the `ImportError`s flow.
    install_requires = [     # dependencies
      # 'bottle>=0.11.6',
      # 'munkres>=1.0.5.4',
      # 'numpy>=1.7.1',
      # 'pandas>=0.12.0',
    ],
)
