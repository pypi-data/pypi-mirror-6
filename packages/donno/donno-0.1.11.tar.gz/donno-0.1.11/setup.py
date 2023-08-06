import multiprocessing

from setuptools import setup

def readme():
    with open('README.md') as f:
        readme = f.read()
    return readme

setup(name='donno',
      version='0.1.11',
      description='A personal CLI note-taking app',
      long_description=readme(),
      classifiers=[
        'Operating System :: POSIX :: Linux',
        'Environment :: Console',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers',
        'Topic :: Text Editors :: Text Processing'
      ],
      keywords='command-line, note-taking, linux',
      url='https://bitbucket.org/leechau/donno',
      author='Li Chao',
      author_email='leechau@126.com',
      license='MIT',
      packages=['donno'],
      entry_points = {
          'console_scripts': ['dn=donno.donno:main'],
      },
      install_requires=[
            "PyYAML>=3.10",
            "argparse>=1.2.1",
            "dropbox>=2.0.0",
            "nltk>=2.0.4",
            "nose>=1.3.0",
            "urllib3>=1.7.1",
            "wsgiref>=0.1.2",
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
