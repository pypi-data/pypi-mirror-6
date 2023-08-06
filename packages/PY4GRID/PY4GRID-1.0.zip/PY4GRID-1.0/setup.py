from setuptools import setup, Extension

ext_mod = []

email = 'joaojfarias@gmail.com'
myname = 'João Jorge Pereira Farias Junior'

long_desc = '''
import random
import org.py4grid.GP as gp


def testando(lista):
    for x in range(2 * 1):
        lista.append(random.random())
    return lista


if __name__ == '__main__':

    from multiprocessing.dummy import Pool as pool
    remote = gp.RemoteProcess(pool, file=__file__)

    ret = remote.processwork(__file__, testando, [[], [], [], []],
                             relative_path={'Darwin': '/Dropbox/BIBLIOTECA_PYTHON', 'Linux': '/Dropbox/BIBLIOTECA_PYTHON'},
                             hosts=[('localhost', 4680)])

    for item in ret:
        for sub in item:
            print(len(sub), sub)
'''

long_desc += '\n\n'
long_desc += '''
before use this framework, 
starts PY4GRIDSERVER generated in PythonXX\Script directory for begin a server

example:

C:\Python33\Script\PY4GRIDSERVER <- starts the server on the default port 4680
'''

setup(name="PY4GRID",
      version="1.0",
      author=myname,
      author_email=email,
      maintainer=myname,
      maintainer_email=email,
      py_modules=['org.py4grid.GP', 'org.py4grid.GPR', 'org.py4grid.remoteserver'],
      ext_modules=ext_mod,
      entry_points={'console_scripts': [
            'PY4GRIDSERVER = org.py4grid:main',
        ]
      },
      description='a little framework to simule multiprocessing over a lot of computers',
      long_description=long_desc,
      classifiers=[
          'Topic :: System :: Distributed Computing',
          'Topic :: Software Development :: Libraries :: Application Frameworks',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
      ]
)
