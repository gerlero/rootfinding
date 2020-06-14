#!/usr/bin/env python

import setuptools

import rootfinding

extras = {
    'publish': ['setuptools', 'wheel', 'twine']
}
extras['dev'] = extras['publish']

setuptools.setup(
    name='rootfinding',
    version=rootfinding.__version__,
    author="Gabriel S. Gerlero",
    author_email="ggerlero@cimec.unl.edu.ar",
    description=rootfinding.__doc__,
    long_description=rootfinding.__doc__,
    url="https://github.com/gerlero/rootfinding",
    project_urls={
        'Bug Tracker': "https://github.com/gerlero/rootfinding/issues",
        'Source Code': "https://github.com/gerlero/rootfinding",
    },
    py_modules=['rootfinding'],
    license='BSD',
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Intended Audience :: Developers',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: BSD License',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Topic :: Scientific/Engineering :: Mathematics',
                 'Topic :: Software Development :: Libraries',
                 'Operating System :: OS Independent'],
    extras_require=extras,
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
    options={'bdist_wheel': {'universal': '1'}}
)