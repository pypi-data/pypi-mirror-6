# W. H. Bell
#
# A Scratch interface, to be used with RpiScratchIO
# The class inherits from RpiScratchIO, to provide
# access to motors and sensors

import sys,threading,time
from BrickPi import *
from RpiScratchIO.Devices import GenericDevice

#=====================================

# For the chip of the same name
class BrickPiScratch(GenericDevice):

  def __init__(self,deviceName_,scratchIO_,connections_,readPeriod_=0,automaticChannels_="none"):

    # Call the base class constructor
    super(BrickPiScratch, self).__init__(deviceName_,scratchIO_,connections_)

    # This is used to trigger readout from the ioThread function.
    # (If the value is zero, it is disabled.)
    self.readPeriod = int(readPeriod_)

    # List of automatic sensors to be updated.
    self.automaticUpdate = []

    # Add the channels to Scratch
    self.sensorChannels = []
    self.encoderChannels = []
    for i in xrange(4):
      self.sensorChannels += [ i ]      # Sensors
      self.outputChannels += [ i+10 ]   # Motors 
      self.encoderChannels += [ i+20 ]   # Encoders
    self.inputChannels += self.sensorChannels
    self.inputChannels += self.encoderChannels

    # Active sensors, motors and motor encoders
    self.activeChannels = {}
    for i in self.inputChannels:
      self.activeChannels[i] = False
    for i in self.outputChannels:
      self.activeChannels[i] = False

    # BrickPi port ids
    self.__portIdsSensors = [ PORT_1, PORT_2, PORT_3, PORT_4 ]
    self.__portIdsMotors = [ PORT_A, PORT_B, PORT_C, PORT_D ]

    # Read the list of attached sensors
    self.__haveSensors = False
    self.__parseConfigFile() 

    # Open serial port connection
    ret_val = BrickPiSetup()
    if ret_val != 0:
      raise Exception("ERROR: could not open serial port link to the BrickPi.  Check the serial port configuration and hardware.")

    # Setup the sensors, if requested
    if self.__haveSensors:
      ret_val = BrickPiSetupSensors()
      if ret_val != 0:
        raise Exception("ERROR: coult not send sensor types to the BrickPi.")

      # If requested, add some sensors or motor encoders for automatic
      # update by the ioThread.
      self.__addAutomaticChannels(automaticChannels_)

    # Start communication loop between Raspberry Pi and BrickPi
    self.__readoutEvent = 0
    self.__startLink()

  #-----------------------------

  def __addAutomaticChannels(self,channelStr):

    # For case insenstive comparison
    channelStrLower = channelStr.lower()

    # Convert the character string to a channel range or channel
    # number
    channelsToAdd = []
    if channelStrLower.lower() == "none":
      del self.automaticUpdate[:]
      return None
    elif channelStrLower.lower() == "all":
      channelsToAdd += self.inputChannels
    elif channelStrLower.lower() == "m":
      channelsToAdd += self.encoderChannels
    elif channelStrLower.lower() == "s":
      channelsToAdd += self.sensorChannels
    else:
      try:
        channelNumber = int(channelStrLower)
        if channelNumber in self.inputChannels:
          channelsToAdd += [ channelNumber ]
        else:
          print("WARNING: \"%d\" is not a valid channel number" % channelNumber)

      except ValueError:
        print("WARNING: \"%s\" is not a number." % channelStrLower)

    # Enable channels that are active for automatic readout
    for channelNumber in channelsToAdd:
      if self.activeChannels[channelNumber]:
        self.automaticUpdate += [ channelNumber ]

  #-----------------------------

  def __parseConfigFile(self):

    # The sensor names are the name as the variables in BrickPi, but without the "TYPE_SENSOR_" prefix
    allowedSensors = []
    allowedSensors += ["TOUCH","ULTRASONIC_CONT","ULTRASONIC_SS","RCX_LIGHT","COLOR_FULL"]
    allowedSensors += ["COLOR_RED","COLOR_GREEN","COLOR_BLUE","COLOR_NONE","I2C","I2C_9V"]

    print("====== BrickPi ========================")
    print("Port (Ch#) ---------- Sensor name") 
    # Read the configuration file, to find which sensors are connected
    # to which ports.  By default, all motors are enabled and no
    # sensors are enabled.
    if self.scratchIO.config.has_section("BrickPi"):
      for portName, sensorName in self.scratchIO.config.items("BrickPi"):

        if len(portName) != 2:
          print("WARNING: \"%s\" is not a valid port name.  Valid ports are S1-S5 or MA-MD." % portName)
          continue

        # Three bit number : sensor, motor, motor encoder
        connectionType = 0

        # Use the variables in BrickPi
        channelOffet = -999
        portIds = []
        if portName[0] == "S":
          try:
            portNumber = int(portName[1])
          except ValueError:
            print("WARNING: \"%s\" is not a valid port name.  Valid ports are S1-S5 or MA-MD." % portName)
            continue

          portIds = self.__portIdsSensors
          connectionType += 1          
        elif portName[0] == "M":
          portNumber = ord(portName[1])-ord('A')+1 # To match sensors
          portIds = self.__portIdsMotors
          connectionType += 2
        else:
          print("WARNING: \"%s\" is not a valid port name.  Valid ports are S1-S5 or MA-MD." % portName)
          continue 
        
        if portNumber < 0 or portNumber > len(portIds):
          print("WARNING: \"%s\" is not a valid port name.  Valid ports are S1-S5 or MA-MD." % portName)
          continue

        # Get the port id for this port name
        portId = portIds[portNumber-1]
 
        # If this is a sensor, check if the sensor is a valid sensor name.
        if connectionType & 1 == 1:
          foundName = False
          for allowedSensor in allowedSensors:
            if allowedSensor.lower() == sensorName.lower():
              foundName = True
              break

          if not foundName:
            print("WARNING: \"%s\" is not a valid sensor name. Valid sensor names are %s." % sensorName, allowedSensors)
            continue

          exec "sensorValue = TYPE_SENSOR_%s" % sensorName

          # Add this sensor
          BrickPi.SensorType[portId] = sensorValue

          # Activate this channel
          self.__activateAndPrint(portName,portNumber-1,sensorName)          
          
        
        # If this a motor, then enable the motor and check if the encoder should be enabled 
        elif connectionType & 2 == 2:
          BrickPi.MotorEnable[portId] = 1
          self.__activateAndPrint(portName,portNumber-1+10,"ON")

        else:
          print("WARNING: unknown connection type!")
          continue
 
    print("=======================================")

  #-----------------------------

  def __brickPiSensorValue(self,channelNumber):
    if channelNumber < 10:
      # This should be safe, since the channelNumber is beforehand
      portId = self.__portIdsSensors[channelNumber]
      value = BrickPi.Sensor[portId]
    else:
      # This should be safe, since the channelNumber is beforehand
      portId = self.__portIdsMotors[channelNumber-20]
      value = BrickPi.Encoder[portId]/2   # print the encoder degrees

    return value

  #-----------------------------

  def __activateAndPrint(self,portName,channelNumber,sensorName):
    self.activeChannels[channelNumber] = True
    # If it is a motor, enable the encoder channel too.
    if channelNumber >= 10:
      self.activeChannels[channelNumber+10] = True
    print("%4s (%3d) ---------- %s " % (portName,channelNumber,sensorName))

    # Make sure the values are flushed to the BrickPi
    if not self.__haveSensors:
      self.__haveSensors = True

  #-----------------------------

  def __startLink(self):
    print(" >> Starting communication with BrickPi")
    self.shutdown_flag = False
    self.server_thread = threading.Thread(target=self.ioThread)
    self.server_thread.start()

  #-----------------------------

  def ioThread(self):
    while not self.shutdown_flag:
      if BrickPiUpdateValues() == 0:
        self.__readoutEvent = self.__readoutEvent + 1

        # Check if the values should be given to scratch or not.
        if self.readPeriod > 0:
          if self.__readoutEvent % self.readPeriod == 0:

            # Loop over all of the channels that should be sent
            # straight back to Scratch.
            for channelNumber in self.automaticUpdate:

              # Get the BrickPi sensor value for this channel
              value = self.__brickPiSensorValue(channelNumber)

              #print("ioThread %d %d" % (channelNumber,value))

              # Send the value back to Scratch
              self.updateSensor(channelNumber, value)

            # Tell scratch that an updated value is available from any
            # of the sensors that are enabled for continuous readout.
            broadcast_msg = "%s:trig" % self.deviceName
            self.scratchIO.scratchHandler.scratchConnection.broadcast(broadcast_msg)

        # If the number is bigger than the maximum size of an integer,
        # then go back to zero
        if self.__readoutEvent >= sys.maxint:
          self.__readoutEvent = 0

      time.sleep(.1)


  #-----------------------------

  def cleanup(self):
    self.shutdown_flag = True
    time.sleep(.2)
    # close the serial link here?

  #-----------------------------

  def config(self,argList):
    nargs = len(argList)
    if nargs == 0:
      print("WARNING: \"config\" expects at least one argument.  No arguments were given")
      return None
    if argList[0] == "update":
      if nargs == 1:
        print("WARNING:device %s expects \"all\", \"s\", \"m\", \"none\" or channel number after \"update\"" % self.deviceName)
        return None
      for arg in argList[1:]:
         self.__addAutomaticChannels(arg)
    elif argList[0] == "period":
      if nargs == 1:
        print("WARNING:device %s expects an integer number after \"period\"" % self.deviceName)
        return None

      # Convert to integer and catch the type error
      try:
        self.readPeriod = int(argList[1])
      except ValueError:
        print("WARNING: %s is not an integer." % argList[1])
        return None

  #-----------------------------

  def write(self,channelNumber,value):

    # Check if the channel is active or not
    if not self.activeChannels[channelNumber]:
      print("WARNING: channel %d of %s is disabled" % (channelNumber,self.deviceName))
      return None

    # Convert to integer and catch the type error
    try:
      intValue = int(value)
    except ValueError:
      print("WARNING: %s is not an integer." % value)
      return None

    # Prevent the value from going out of range.
    if intValue < -255:
      intValue = -255
    elif intValue > 255:
      intValue = 255

    # This should be safe, since the channelNumber is beforehand
    portId = self.__portIdsMotors[channelNumber-10]

    #print("Write %d %d" % (portId,intValue))

    # Set the motor speed value
    BrickPi.MotorSpeed[portId] = intValue

    # Get the last event number, to check for a new value
    lastReadout = self.__readoutEvent

    # Wait for a new value
    counter = 0
    while lastReadout == self.__readoutEvent and counter < 20:
      time.sleep(0.05)
      counter = counter + 1

    # Check if the update was successful or not
    if counter == 20:
      print("WARNING: %s is unable to set motor values" % self.deviceName)
      return None

    # Set the scratch sensor value for this motor
    self.updateSensor(channelNumber,intValue)

  #-----------------------------

  def read(self,channelNumber):

    # Check if the channel is active or not
    if not self.activeChannels[channelNumber]:
      print("WARNING: channel %d of %s is disabled" % (channelNumber,self.deviceName))
      return None

    # Get the last event number, to check for a new value
    lastReadout = self.__readoutEvent 

    # Wait for a new value
    counter = 0
    while lastReadout == self.__readoutEvent and counter < 20:
      time.sleep(0.05)
      counter = counter + 1

    if counter == 20:
      print("WARNING: %s is unable to retrieve sensor values" % self.deviceName)
      return None

    # Get the sensor value that matches this channel number
    value = self.__brickPiSensorValue(channelNumber)

    # Send the value back to Scratch
    self.updateSensor(channelNumber, value)

#=====================================
