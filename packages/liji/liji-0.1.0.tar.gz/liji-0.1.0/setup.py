# -*- coding: utf-8 -*-

import os
from setuptools import setup, Extension


if not 'CFLAGS' in os.environ:
    os.environ['CFLAGS'] = ''

setup(
    name='liji',
    version='0.1.0',
    description="liji",
    keywords='json',
    author='globo.com',
    author_email='cezarsa@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7'
    ],
    packages=['liji'],
    package_dir={"liji": "liji"},
    include_package_data=True,
    install_requires=[
    ],
    ext_modules=[
        Extension('liji.ext._liji',
                  ['liji/ext/_liji.c', 'lib/liji.c'],
                  include_dirs=['lib'],
                  depends=['setup.py', 'liji/ext/_liji.c', 'lib/liji.c', 'lib/liji.h'],
                  extra_compile_args=['-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter'])
    ]
)
