# SASS_Pi_Package
Smart Automated Shower System (SASS) - Raspberry Pi 3B
This is a two microprocessor system that uses a Raspberry Pi 3B to handle the GUI, high-level logic, networking, and data storage.
While using a Arduino Uno for collecting sensor data, actuating solenoids, commanding servos, creating averages, and other low-level logic.
Both microcontrollers communicate via Serial and send structured messages that (raspi) send command signals to have actions performed or
(arduino) send sensor data and averages back to be displayed in the GUI and saved to a database for later.

This code is specificly for running on a Raspberry Pi 3B in conjunction with the Raspberry Pi 7 inch touch display.
The Raspi 3B acts the user interface and displays a GUI using Python and Kivy.
Database and major logic functions on completed here. When a user changes a setting via the GUI a variable is changed in the message.
That message with the new command is sent to the Arduino Uno via USB Serial. All sensor data collected by the Arduino is then sent,
periodicly, back to the Raspi in a message similar to that command message from the Raspi.


System requirements to run this code.

Python 3.5.3 - Used to write the main GUI and logic code for SASS
    Command messages to be sent to Arduino and main logic methods were written in Python.
    Kivy, a proprietary markup language, was used to develop the Graphical User Interface

    Python Packages Installed
        certifi==2018.8.24
        chardet==3.0.4
        cryptography==1.7.1
        Cython==0.27.3
        docutils==0.14
        future==0.16.0
        idna==2.7
        iso8601==0.1.12
        keyring==10.1
        keyrings.alt==1.3
        Kivy==1.10.1
        Kivy-Garden==0.1.4
        pyasn1==0.1.9
        pycrypto==2.6.1
        pygame==1.9.4
        Pygments==2.2.0
        pygobject==3.22.0
        pymata-aio==2.25
        pyserial==3.4
        python-apt==1.1.0b5
        pyxdg==0.25
        PyYAML==3.13
        requests==2.19.1
        SecretStorage==2.3.1
        six==1.10.0
        urllib3==1.23
        websockets==6.0


Helpful links
  Arduino Serial Input Basics - https://forum.arduino.cc/index.php?topic=396450.0

Some basic Raspberry Pi help if needed.

  Setting up Raspberry Pi
    Load SD card with Raspbian core
    Put card in Raspi and power it
    User: pi
    Password: raspberry
    Run the following commands to complete updates
    sudo apt-get update
    sudo apt-get upgrade
    Sudo pip3 install --upgrade pip
    Sudo pip3 freeze (this checks what packages are installed)
    Sudo pip3 install git+https://github.com/kivy/kivy.git@sta
    ble-1.10
    Sudo rpi-update
    Do the following to get the touch screen working
    Nano ~/.kivy/config.ini
    Navigate down to [input] and change hidinput to mtdev
    %(name)s = probesysfs,provider=mtdev
