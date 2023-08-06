#!/usr/bin/env python
# Copyright (c) 2013 krishna.srinivas@gmail.com All rights reserved.
# This script is part of nutty.io project
# GPLv3 License <http://www.gnu.org/licenses/gpl.txt>

import os
from distutils.core import setup
from distutils.command.install_data import install_data

jsonfile1 = '{\n\
  "name": "io.nutty.terminal",\n\
  "description": "nutty.io - Securely share terminals over web using browser",\n'

jsonfile3 = '  "type": "stdio",\n\
  "allowed_origins": [\n\
    "chrome-extension://ooelecakcjobkpmbdnflfneaalbhejmk/"\n\
  ]\n\
}\n\
'

jsonfile = ''

if os.uname()[0] == 'Darwin':
    if os.getuid() == 0:
        scriptdir = '/usr/local/bin/'
        chromenativedir = '/Library/Google/Chrome/NativeMessagingHosts'
        chromiumnativedir = '/Library/Application Support/Chromium/NativeMessagingHosts'
    else:
        scriptdir = os.environ['HOME'] + '/.nutty/'
        chromenativedir = os.environ['HOME'] + '/Library/Application Support/Google/Chrome/NativeMessagingHosts'
        chromiumnativedir = os.environ['HOME'] + '/Library/Application Support/Google/Chromium/NativeMessagingHosts'
else:
    if os.getuid() == 0:
        scriptdir = '/usr/local/bin/'
        chromenativedir = '/etc/opt/chrome/native-messaging-hosts'
        chromiumnativedir = '/etc/chromium/native-messaging-hosts'
    else:
        scriptdir = os.environ['HOME'] + '/.nutty/'
        chromenativedir = os.environ['HOME'] + '/.config/google-chrome/NativeMessagingHosts'
        chromiumnativedir = os.environ['HOME'] + '/.config/chromium/NativeMessagingHosts'

chromescriptfile = scriptdir + 'nutty-chrome.sh'
chromiumscriptfile = scriptdir + 'nutty-chromium.sh'

chromejsonfile2 = '  "path": "' + chromescriptfile + '",\n'
chromiumjsonfile2 = '  "path": "' + chromiumscriptfile + '",\n'

chromejsonfile = jsonfile1 + chromejsonfile2 + jsonfile3
chromiumjsonfile = jsonfile1 + chromiumjsonfile2 + jsonfile3

chromejsonfile = chromejsonfile.replace('io.nutty.terminal', 'io.nutty.chrome')
chromiumjsonfile = chromiumjsonfile.replace('io.nutty.terminal', 'io.nutty.chromium')

with open('io.nutty.chrome.json', 'w') as outfile:
    outfile.write(chromejsonfile)

with open('io.nutty.chromium.json', 'w') as outfile:
    outfile.write(chromiumjsonfile)

class my_install(install_data):
    def run(self):
        install_data.run(self)
        os.chmod(scriptdir + '/nutty-chrome.sh', 493)
        os.chmod(scriptdir + '/nutty-chromium.sh', 493)

setup(
    name='nutty',
    version='1.0.0',
    description='Share terminals using browser',
    author='Krishna Srinivas',
    author_email='krishna.srinivas@gmail.com',
    url='https://nutty.io',
    license='GPLv3',
    data_files=[(chromenativedir, ['io.nutty.chrome.json']),
                (chromiumnativedir, ['io.nutty.chromium.json']),
                (scriptdir,['nutty-chrome.sh', 'nutty-chromium.sh'])],
    cmdclass=dict(install_data=my_install)
    )

