""" Setup file for distutils

"""

from distutils.core import setup

setup(
    name='pyonedrive',
    version='1.0',
    author='Tony Sanchez',
    author_email='mail.tsanchez@gmail.com',
    url='https://github.com/tsanch3z/pyonedrive',
    download_url='https://github.com/tsanch3z/pyonedrive/archive/master.zip',
    description='Onedrive REST api client',
    packages=['pyonedrive'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Web Environment',
        'Development Status :: 4 - Beta'
    ],
    install_requires='requests>=2.2.1'
)
