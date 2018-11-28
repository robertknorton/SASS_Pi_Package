#!/usr/bin/python3

# Author: Robert Norton
# Project: Senior Design Project: Smart Automated Shower System (SASS)
# Date Last Updated: 11/27/2018

from subprocess import call
# with open('/home/pi/sass/log.txt', 'w') as f: call(['python3', '/home/pi/sass/main.py'], stdout=f)
call('python3 /home/pi/sass/main.py'.split())