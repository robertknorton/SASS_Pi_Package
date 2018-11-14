#!/usr/bin/python3
import os
import sys
import kivy
kivy.require('1.10.1')

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.treeview import TreeView, TreeViewLabel, TreeViewNode
from kivy.config import Config

import sqlite3
from sqlite3 import Error

import serial as ser
import string
import time
from datetime import datetime
import ctypes

#=======================================================================================================================

board = ser.Serial(port='/dev/ttyACM0',
                   baudrate=115200,
                   parity=ser.PARITY_NONE,
                   timeout=4)

# Configuring window size
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')

numChars = 32
recievedChars = [None] * numChars
tempChars = [None] * numChars


#=======================================================================================================================

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def checkMemory(*args):
    tot_m, used_m, free_m = map(int, os.popen('free -t -m').readlines()[-1].split()[1:])
    print(time.strftime('%I' + ':' + '%M' + ' %p'))
    print('Total Memory = ' + str(tot_m) + ' MB')
    print('Used Memory = ' + str(used_m) + ' MB')
    print('Free Memory = ' + str(free_m) + ' MB')

def checkCPU(*args):
    """ Returns a list CPU Loads"""
    result = []
    cmd = "WMIC CPU GET LoadPercentage "
    response = os.popen(cmd + ' 2>&1','r').read().strip().split("\r\n")
    for load in response[1:]:
       result.append(int(load))
    print(result)

#--------------Data base functions-----------------

def connect_database(name, *args):
    try:
        conn = sqlite3.connect(name)
    except sqlite3.DatabaseError as e:
        raise e
    else:
        print('DB Connection Established')
        return conn

def create_table(conn, *args):
    cur = conn.cursor()
    try:
        cur.execute('CREATE TABLE IF NOT EXISTS Shower('
                    '"Shower Date"    Text PRIMARY KEY NOT NULL,'  # Storing shower time and day
                    '"Start Time"     Text NOT NULL,'
                    '"End Time"       Text NOT NULL,'
                    '"Total Time On"  Text NOT NULL,'
                    '"AVG Water Temp" Text NOT NULL,'
                    '"Total Water Used" Text NOT NULL)')
    except Error as e:
        conn.rollback()
        raise e

def insert_table(conn, content):
    try:
        cur = conn.cursor()
        cur.execute("insert into Shower VALUES (?,?,?,?,?,?)", content)
    except sqlite3.DatabaseError as e:
        conn.rollback()
        raise e
    else:
        conn.commit()

def select_query(conn):
    try:
        cur = conn.cursor()
        cur.execute("SELECT * From Shower")
    except Error as e:
        raise e
    else:
        return cur.fetchall()

def close_conn(dbconn):
    try:
        dbconn.commit()
    except Error as e:
        dbconn.rollback()
        raise e
    finally:
        print('Database has been closed')
        dbconn.close()

#--------------------------------------------------

#=======================================================================================================================

# class StartButton(Button):
#     def on_release(self):
#         Controller.STV = 1
#         if Controller.timer_initial == 0:
#             Controller.timer_initial = datetime.now() # sets initial interval time
#             Controller.shower_time_start = datetime.now() # save the start time
#             # initializes a timer_total of time timedelta with a value of all zeros
#             Controller.timer_total = Controller.timer_initial - Controller.timer_initial

# class StopButton(Button):
#     def on_release(self):
#         Controller.STV = 0
#         # print(Controller.FS)
#         Controller.FS = 0
#         # print(Controller.FS)

# class ResetButton(Button):
#     def on_release(self):
#         Controller.shower_time_end = datetime.now()
#         Controller.insert(Controller.root) # this inserts a shower event data entry
#         Controller.RST = 1
#         Controller.STV = 0
#         Controller.FS = 0
#         Controller.timer_initial = 0 # resets value for next shower
#         Controller.timer_total = 0 # resets vale for next shower
#         Controller.WT = 0  # water temp
#         Controller.WTA = 0  # water temp avg
#         Controller.FL = 0  # water flow
#         Controller.FLT = 0  # water flow total

class ProximitySwitch(Switch):
    pass

class AutoWarmSwitch(Switch):
    pass

class FlowSlider(Slider):
    def on_touch_up(self, touch):
        Controller.FS = round(self.value,2)
        # print(Controller.FS)

class TempSlider(Slider):
    def on_touch_up(self, touch):
        Controller.TS = round(self.value,2)
        # print(Controller.TS)

class WaterTempLabel(Label):
    def update(self, WT, *args):
        self.text = str(WT) + u'\N{DEGREE SIGN}F'

class WaterTempAvgLabel(Label):
    def update(self, WTA, *args):
        self.text = str(WTA) + u'\N{DEGREE SIGN}F'

class WaterFlowLabel(Label):
    def update(self, FL, *args):
        self.text = str(FL) + u' gal/m'

class WaterTotalLabel(Label):
    def update(self, FLT, *args):
        self.text = str(FLT) + u' gal'

# This is a custom clock widget the is used to display the system time on the control panel
# class SystemClock(Label):
#     def updateClock(self, *args):
#         self.text = time.strftime('%I' + ':' + '%M' + ' %p')

# This is a timer clock for how long the current shower has been
# class TimerClock(Label):
#     def update(self, *args):
#         if Controller.timer_initial != 0:
#             if Controller.STV == 1:
#                 Controller.timer_current = datetime.now() # gets the current time
#                 dif = Controller.timer_current - Controller.timer_initial  # get the interval difference
#                 Controller.timer_initial = datetime.now() # this resets the interval time
#                 Controller.timer_total = Controller.timer_total + dif # sums up the interval time to total
#             elif Controller.STV == 0:
#                 Controller.timer_initial = datetime.now() # this makes sure to keep updating initial time for interval
#
#             minutes = int(Controller.timer_total.seconds % 3600 / 60.0)  # calculate the difference in minutes
#             Controller.shower_time_total = str(minutes).zfill(2) + ':' + str(Controller.timer_total.seconds % 60).zfill(2)
#             self.text = Controller.shower_time_total
#         else:
#             self.text = str(0).zfill(2) + ':' + str(0).zfill(2)


# class ShowerEventTree(TreeView):
#     numOfEvents = 0
#     def addEvent(self, *args):
#         self.numOfEvents = self.numOfEvents + 1
#         event = self.TreeView.add_node(TreeViewLabel(text='SE'+ str(self.numOfEvents), is_open=True))
#         awt = self.TreeView.add_node(TreeViewLabel(text=str('Avg Water Temp')), event)
#         self.TreeView.add_node(TreeViewLabel(text=str(Controller.WTA)), awt)
#         twu = self.TreeView.add_node(TreeViewLabel(text=str('Total Water Used')), event)
#         self.TreeView.add_node(TreeViewLabel(text=str(Controller.FLT)), twu)

#=======================================================================================================================

class Controller(TabbedPanel):

    sendInputs = False

    # Controls Tab Object Properties
    sys_clock = ObjectProperty()
    timer_clock = ObjectProperty()
    start_button = ObjectProperty()
    stop_button = ObjectProperty()
    reset_button = ObjectProperty()
    proximity_switch = ObjectProperty()
    auto_warm_cool_switch = ObjectProperty()
    flow_slider = ObjectProperty()
    temp_slider = ObjectProperty()
    water_temp_label = ObjectProperty()
    water_flow_label = ObjectProperty()
    water_temp_avg_label = ObjectProperty()
    water_total_label = ObjectProperty()

    # Programs Tab Object Properties

    # Logs Tab Object Properties
    sort_drop_down = ObjectProperty()
    sort_up_down = ObjectProperty()
    rv = ObjectProperty()

    # Control Variables
    STV = 0
    BPV = 0
    RST = 0
    FS = 0
    TS = 68

    # Sensor Variables
    WT = 0      # water temp
    WTA = 0     # water temp avg
    FL = 0      # water flow
    FLT = 0     # water flow total
    PRX = 0     # proximity

    # Timer Variables
    timer_initial = 0
    timer_current = 0
    timer_total = 0

    # Extra Event Data
    shower_time_start = 0
    shower_time_end = 0
    shower_time_total = 0

    def __init__(self, **kwargs):
        super(Controller, self).__init__(**kwargs)
        # Clock.schedule_interval(self.update, 0.5)
        # Clock.schedule_interval(checkMemory, 10)
        # Clock.schedule_interval(checkCPU, 10)
        # Clock.schedule_interval(self.sys_clock.update, 2)
        Clock.schedule_interval(self.updateClock, 2)
        Clock.schedule_interval(self.updateTimerClock, 0.9)
        Clock.schedule_interval(self.read_sensors, 1)
        Clock.schedule_interval(self.send_input, 1)

        # Control Variables
        self.STV = 0
        self.BPV = 0
        self.RST = 0
        self.FS = 0
        self.TS = 68

        # Sensor Variables
        self.WT = 0  # water temp
        self.WTA = 0  # water temp avg
        self.FL = 0  # water flow
        self.FLT = 0  # water flow total
        self.PRX = 0  # proximity

        # Timer Variables
        self.timer_initial = 0
        self.timer_current = 0
        self.timer_total = 0

        # Extra Event Data
        self.shower_time_start = 0
        self.shower_time_end = 0
        self.shower_time_total = 0
        self.eventData = []
        # self.contEventTime = [] # this is a list of time marker readings
        # self.contEventTemp = [] # this is a list of water temp readings
        # self.contEventWater = [] # this is a list of total water used readings


    # def update(self, *args):
    #     self.read_sensors()
    #     if self.sendInputs == True:
    #         self.send_input()

    # def update_cont_vars(self, *args):
    #     self.contEventTime.append(self.timer_clock.text)
    #     self.contEventTemp.append(self.WT)
    #     self.contEventWater.append(self.FLT)


    def read_sensors(self, *args):
        serial_line = board.readline().rstrip().decode()
        if len(serial_line) > 1:
            if serial_line[0] == '{' and serial_line[len(serial_line)-1] == '}':
                tempData1 = serial_line[:-1] # trim last }
                tempData2 = tempData1[1:] # trim first {
                parsedData = tempData2.split(',') # parse the data values
                print(parsedData)
                # Update variables
                self.WT = int(parsedData[0])
                self.WTA = int(parsedData[1])
                self.FL = int(parsedData[2]) / 100
                self.FLT = int(parsedData[3]) / 100
                self.PRX = int(parsedData[4])
                # Update GUI values
                # print(self.FLT)
                self.water_temp_label.update(self.WT)
                self.water_temp_avg_label.update(self.WTA)
                self.water_flow_label.update(self.FL)
                self.water_total_label.update(self.FLT)

    def send_input(self, *args):
        # print(self.auto_warm_cool_switch.active)
        # print(Controller.TS)
        # print(self.WT)
        if (self.auto_warm_cool_switch.active == True) and (self.STV == 1): # if shower is on and the auto switch is active
            if int(Controller.TS) == int(self.WT): # if the set temp and actual measured temp are equal do...
                self.STV = 0 # turn off system
                Controller.FS = 0 # set water flow to 0
                self.flow_slider.value = Controller.FS  # updates GUI slider widget
                self.auto_warm_cool_switch.active = False # turn auto switch to False(off)
            else:
                Controller.FS = 100 # Open valve completely to allow water to flow and temperature to change
                self.flow_slider.value = Controller.FS  # updates GUI slider widget

        elif (self.proximity_switch.active == True) and (self.STV == 1): # only runs proximity sensor when system on
            if int(self.PRX) < 15:
                Controller.FS = 100
            elif int(self.PRX) < 20:
                Controller.FS = 60
            elif int(self.PRX) < 25:
                Controller.FS = 30
            elif int(self.PRX) < 30:
                Controller.FS = 0
            else:
                pass
            self.flow_slider.value = Controller.FS
        else:
            self.flow_slider.value = Controller.FS

        newFS = translate(Controller.FS,0,100,0,100) # make sure this is getting Controller.FS or it will not work
        newTS = translate(Controller.TS, 68,110,0,100) # make sure this is getting Controller.TS or it will not work
        # print(type(self.FS))
        # print(self.FS)
        # print(type(Controller.FS))
        # print(Controller.FS)
        newInput = str("<"+str(self.STV)+","+str(self.BPV)+","+str(self.RST)+","+str(round(newFS))+","+str(round(newTS))+">")
        # print(newInput)
        board.write(newInput.encode())
        self.sendInputs = False
        self.RST = 0

    # --------- Controls Stuff --------------

    def updateClock(self, *args):
        self.sys_clock.text = time.strftime('%I' + ':' + '%M' + ' %p')

    def updateTimerClock(self, *args):
        if self.timer_initial != 0:
            if self.STV == 1:
                self.timer_current = datetime.now() # gets the current time
                dif = self.timer_current - self.timer_initial  # get the interval difference
                self.timer_initial = datetime.now() # this resets the interval time
                self.timer_total = self.timer_total + dif # sums up the interval time to total
            elif self.STV == 0:
                self.timer_initial = datetime.now() # this makes sure to keep updating initial time for interval

            minutes = int(self.timer_total.seconds % 3600 / 60.0)  # calculate the difference in minutes
            self.shower_time_total = str(minutes).zfill(2) + ':' + str(self.timer_total.seconds % 60).zfill(2)
            self.timer_clock.text = self.shower_time_total
        else:
            self.timer_clock.text = str(0).zfill(2) + ':' + str(0).zfill(2)

    def startShower(self):
        self.STV = 1
        if self.timer_initial == 0:
            self.timer_initial = datetime.now() # sets initial interval time
            self.shower_time_start = datetime.now() # save the start time
            # initializes a timer_total of time timedelta with a value of all zeros
            self.timer_total = self.timer_initial - self.timer_initial

    def stopShower(self):
        self.STV = 0
        # print(Controller.FS)
        self.FS = 0
        # print(Controller.FS)

    def resetShower(self):
        if self.STV != 1:
            self.shower_time_end = datetime.now()
            self.insert() # this inserts a shower event data entry

            self.RST = 1
            self.STV = 0
            self.FS = 0
            self.timer_initial = 0  # resets value for next shower
            self.timer_total = 0    # resets vale for next shower
            self.WT = 0  # water temp
            self.WTA = 0  # water temp avg
            self.FL = 0  # water flow
            self.FLT = 0  # water flow total

    #--------- Logs Stuff --------------

    def sortLog(self, text, direction): # This function sorts the data log table by which ever type is selected to sort
        # sortedEventData = []
        if direction == 'Ascending':
            dir = False
        else: # Descending order
            dir = True
        if text == 'Date':
            sortedEventData = sorted(self.eventData, key=lambda event: event[0], reverse=dir)  # sort by event date
            self.rv.data = [{'value': y} for x in sortedEventData for y in x]
            self.eventData = sortedEventData
        elif text == 'Start Time':
            sortedEventData = sorted(self.eventData, key=lambda event: event[1], reverse=dir)  # sort by event start time
            self.rv.data = [{'value': y} for x in sortedEventData for y in x]
            self.eventData = sortedEventData
        elif text == 'End Time':
            sortedEventData = sorted(self.eventData, key=lambda event: event[2], reverse=dir)  # sort by event end time
            self.rv.data = [{'value': y} for x in sortedEventData for y in x]
            self.eventData = sortedEventData
        elif text == 'Total Time On':
            sortedEventData = sorted(self.eventData, key=lambda event: event[3], reverse=dir) # sort by event total time on
            self.rv.data = [{'value': y} for x in sortedEventData for y in x]
            self.eventData = sortedEventData
        elif text == 'Avg Water Temp':
            sortedEventData = sorted(self.eventData, key=lambda event: event[4], reverse=dir) # sort by event avg water temp
            self.rv.data = [{'value': y} for x in sortedEventData for y in x]
            self.eventData = sortedEventData
        elif text == 'Most Water Used':
            sortedEventData = sorted(self.eventData, key=lambda event: event[5], reverse=dir) # sort by event total water used
            self.rv.data = [{'value': y} for x in sortedEventData for y in x]
            self.eventData = sortedEventData
        else:
            pass
        self.sort_drop_down.text = 'Sort Type'


    def clear(self):
        self.rv.data = []


    def insert(self):

        if (self.shower_time_start != 0):
            st = ('%02d:%02d:%02d' % (self.shower_time_start.hour, self.shower_time_start.minute, self.shower_time_start.second))
            et = ('%02d:%02d:%02d' % (self.shower_time_end.hour, self.shower_time_end.minute, self.shower_time_end.second))
            self.eventData.append((str(self.shower_time_start.date()), str(st), str(et), str(self.shower_time_total),str(self.WTA), str(self.FLT)))
            self.rv.data = [{'value': y} for x in self.eventData for y in x]

            Db = connect_database('SASS.db')
            insert_table(Db, (str(self.shower_time_start),str(st),str(et),str(self.shower_time_total),str(self.WTA),str(self.FLT)))
            close_conn(Db)
            self.shower_time_start = 0 # to make sure it doesnt try to upload to data base again

    def update(self, value):
        if self.rv.data:
            self.rv.data[0]['value'] = value or 'default new value'
            self.rv.refresh_from_data()

    def remove(self):
        if self.rv.data:
            self.rv.data.pop(0)

    def restartProgram(*args):
        print('Restarting')
        os.execv(sys.executable, ['python3', 'main.py'])

    def rebootSystem(*args):
        print('Rebooting')
        os.system('sudo reboot now')

    def shutdownSystem(*args):
        print('Shutdown')
        os.system('sudo shutdown now')


#=======================================================================================================================

class ControllerApp(App):

    def build(self):
        self.title = "Smart Automated Shower System"
        ctrl = Controller()
        
        return ctrl


if __name__ == '__main__':
    ControllerApp().run()




