#!/usr/bin/python3
from subprocess import call
# with open('/home/pi/sass/log.txt', 'w') as f: call(['python3', '/home/pi/sass/main.py'], stdout=f)
call('python3 /home/pi/sass/main.py'.split())