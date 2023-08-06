from setuptools import setup

name = 'João Jorge Pereira Farias Junior'
email = 'joaojfarias@gmail.com'

long_desc = '''

import random
import org.py4grid.GP as gp


def testando(lista):
    for x in range(2 * 1):
        lista.append(random.random())
    return lista


if __name__ == '__main__':

    from multiprocessing.dummy import Pool as pool
    remote = gp.RemoteProcess(pool, file=__file__, discover_hosts=True)

    ret = remote.processwork(__file__, testando, [[], [], [], []],
                             relative_path={'Darwin': '/Dropbox/BIBLIOTECA_PYTHON', 'Linux': '/Dropbox/BIBLIOTECA_PYTHON'},
                             Hosts=[('localhost', 4680)])

    for item in ret:
        for sub in item:
            print(len(sub), sub)




before use this framework, 
starts PY4GRIDSERVER generated in PythonXX\Script directory for begin a server
and then start DISCOVER if you want to use the option discover_hosts, this option works discovering the address of the servers started
and only works if the Hosts argument is empty, if you do not wish to use this option must explicitly pass the argument Hosts

example:

C:\Python33\Script\PY4GRIDSERVER <- starts the server on port 4680
C:\Python33\Script\DISCOVER <- start the discoverer of servers

'''

setup(name="PY4GRID",
      version="1.0.2",
      author=name,
      author_email=email,
      maintainer=name,
      maintainer_email=email,
      packages=['org.py4grid', 'org.py4grid.multicast', 'org.py4grid.multicast.daemons', 'org.py4grid.scripts'],
      entry_points={'console_scripts': [
            'PY4GRIDSERVER = org.py4grid.scripts.exec:p4s_main',
            'DISCOVER = org.py4grid.scripts.exec:ds_main'
        ]
      },
      description='a little framework to simule multiprocessing over a lot of computers',
      long_description=long_desc,
      license='GPLv3+',
      classifiers=[
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Topic :: System :: Distributed Computing',
          'Topic :: Software Development :: Libraries :: Application Frameworks',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
      ]
)
