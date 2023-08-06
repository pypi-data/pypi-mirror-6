#!/usr/bin/env python
# Copyright (c) 2013 krishna.srinivas@gmail.com All rights reserved.
# This script is part of nutty.io project
# GPLv3 License <http://www.gnu.org/licenses/gpl.txt>

import os
from distutils.core import setup
from distutils.command.install_data import install_data

if os.uname()[0] == 'Darwin':
    chromenativedir = '/Library/Google/Chrome/NativeMessagingHosts'
    chromiumnativedir = '/Library/Application Support/Chromium/NativeMessagingHosts'
else:
    chromenativedir = '/etc/opt/chrome/native-messaging-hosts'
    chromiumnativedir = '/etc/chromium/native-messaging-hosts'

class my_install(install_data):
    def run(self):
        install_data.run(self)
        os.chmod('/usr/local/bin/nutty.py', 493)
        os.chmod('/usr/local/etc/nutty.conf', 420)

setup(
    name='nutty',
    version='1.2.0',
    description='Share terminals using browser',
    author='Krishna Srinivas',
    author_email='krishna.srinivas@gmail.com',
    url='https://nutty.io',
    license='GPLv3',
    data_files=[(chromenativedir, ['io.nutty.terminal.json']),
                (chromiumnativedir, ['io.nutty.terminal.json']),
                ('/usr/local/etc', ['nutty.conf']),
                ('/usr/local/bin', ['nutty.py'])],
    cmdclass=dict(install_data=my_install)
    )

