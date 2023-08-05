# Copyright (C) 2012 Bob Bowles <bobjohnbowles@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Work around mbcs bug in distutils. (for wininst)
# http://bugs.python.org/issue10945
import codecs
try:
    codecs.lookup('mbcs')
except LookupError:
    ascii = codecs.lookup('ascii')
    func = lambda name, enc = ascii: {True: enc}.get(name == 'mbcs')
    codecs.register(func)

from distutils.core import setup
import os

# automate the list of i18n files

# locale root
targetLocaleRoot = ''
if os.name == 'nt':
    # need to point to the correct root file for the python version
    import sys
    targetLocaleRoot = os.path.dirname(os.path.realpath(sys.executable))
elif os.name == 'posix': targetLocaleRoot = os.path.join('/', 'usr', 'share')

# auto-generate the list of .mo files
languages = os.listdir('locale')
languageFiles = []
for language in languages:
    languageFiles.append((os.path.join(targetLocaleRoot,
                                       'locale',
                                       language,
                                       'LC_MESSAGES'),
                          [os.path.join('locale',
                                        language,
                                        'LC_MESSAGES',
                                        'Reversi.mo'), ]))
dataFiles = languageFiles

# detect Ubuntu/Unity to decide what to do with the launcher
from subprocess import Popen, PIPE
if os.name == 'posix':
    pipe = Popen('ps aux | grep unity', shell=True, stdout=PIPE).stdout

    # now scan the output for some unity tell-tale
    if  'unity-panel-service' in str(pipe.read()):
        print('Ubuntu and Unity detected!')
        dataFiles.append((os.path.join(targetLocaleRoot, 'applications'),
                          ['Reversi.desktop']))
    else:
        # TODO: no launcher for other posix
        print('Posix detected - No Unity')

elif os.name == 'nt':
    # make the bat file install in a vaguely sensible place
    print('Windows detected')

    # NOTE documents and settings still exists on win7, its just hidden.
    publicDesktop = \
        os.path.realpath('C:/Documents and Settings/All Users/Desktop')

    # discriminate between XP and Win7
    if os.path.exists(os.path.realpath('C:/Users')):
        print('Windows 7/8 detected')
        publicDesktop = os.path.realpath('C:/Users/Public/Desktop')
    else:
        print('Windows XP assumed')
    dataFiles.append((publicDesktop, ['Reversi.bat']))

else:
    # no os identified, let's cross our fingers ...
    print('OS not known')

setup(
    name='Reversi',
    version='1.2',
    description='A version of the Reversi board game intended for casual play.',
    long_description=open('README.txt').read(),
    author='Bob Bowles',
    author_email='bobjohnbowles@gmail.com',
    url='http://pypi.python.org/pypi/Reversi',
    license='GNU General Public License v3 (GPLv3)',  # TODO belt-n-braces??
    keywords=["Reversi", "Othello", ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Natural Language :: Chinese (Simplified)",
        "Natural Language :: English",
        "Natural Language :: French",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Microsoft :: Windows :: Windows 7",
        "Topic :: Games/Entertainment :: Board Games",
        "Topic :: Games/Entertainment :: Turn Based Strategy",
        ],
    package_dir={'': 'src'},
    packages=['Reversi', ],
    requires=['numpy (>=1.6.1)', 'tkinter (>=8.5)'],  # TODO needs Python >3.3
    package_data={'Reversi': ['graphics/BWSmiley-75x75.gif',
                              'graphics/WBSmiley-75x75.gif',
                              'graphics/star-75x75.gif',
                              'graphics/unplayed-75x75.gif',
                              ]},
    data_files=dataFiles,
)



