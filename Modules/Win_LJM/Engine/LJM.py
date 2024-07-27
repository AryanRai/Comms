# This script demonstrates how to read/write analog inputs and digital I/O on a LabJack device.
import sys
from labjack import ljm
import time

class LMJlogger:
    A0 = []
    A1 = []
    Relay_Val = []
    time_elapsed = []
    absolute_time = []
    pressurePSI = []
    names = []
    last_draft = None
    last_update = None
    
    def __init__(self, names):
        self.names = names

    #this time is from when program starts not the labjack
    def log_createdraft(self):
        self.values = [self.time_elapsed, self.absolute_time ,self.A0, self.A1, self.Relay_Val, self.pressurePSI] 
        log = (self.names, self.values)
        self.last_draft = log
        self.last_draft_timer = time.time()
        return log

    #this is labjack timing
    def log_add(self, log_time, absolute_time ,A0, A1, Relay_Val, pressurePSI):
        self.time_elapsed.append(log_time)
        self.absolute_time.append(absolute_time)
        self.A0.append(A0)
        self.A1.append(A1)
        self.Relay_Val.append(Relay_Val)
        self.pressurePSI.append(pressurePSI)
        self.last_update = time.time()
        print(str(time.time()) + ": ", "log added") #need to make a global program run timer and use that instead of time.time()

    #example
    #time = [0, 1, 2, 3]
    #A0 = [90, 40, 80, 98]
    #A1 = [90, 40, 80, 98]
    #Relay_Val = [True, False, True, False]

    #names = ['time_elapsed', 'A0', 'A1', 'Relay_Val']
    #values = [time, A0, A1, Relay_Val]

class LMJdevice:
    loopAmount = "infinite"
    loopMessage = ""
    intervalHandle = 1
    handle = None
    info = None
    deviceType = None
    fioState = 0  # 0 or 1
    runner = True
    singleEnded = True
    status = None
    
    

    def __init__(self):
        self.device_connect()
        self.device_setup()
        self.runner = True
        self.status = "Initialized"

    def function_loop(self, count= None):
        if count is None:
            # An argument was not passed. Loop an infinite amount of times.
            self.loopAmount = "infinite"
            self.loopMessage = " Press Ctrl+C to stop."
        else:
            # An argument was passed. The first argument specifies how many times to loop.
            try:
                self.loopAmount = int(count)
            except:
                raise Exception("Invalid argument \"%s\". This specifies how many times to loop and needs to be a number." % str(self.loopAmount))

        # Rest of the code...

        # Call the function with the desired loop amount
        #loop_function(10)  # Example: Loop 10 times

    
    def device_connect(self):
        # Open first found LabJack
        #self.handle = ljm.openS("T7", "ANY", "ANY")  # Any device, Any connection, Any identifier
        self.handle = ljm.openS("T7", "ANY", -2)  # demo modeS
        #handle = ljm.openS("T8", "ANY", "ANY")  # T8 device, Any connection, Any identifier
        #handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier
        #handle = ljm.openS("T4", "ANY", "ANY")  # T4 device, Any connection, Any identifier
        #handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")  # Any device, Any connection, Any identifier
        self.info = ljm.getHandleInfo(self.handle)

        print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
            "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
            (self.info[0], self.info[1], self.info[2], ljm.numberToIP(self.info[3]), self.info[4], self.info[5]))

        self.deviceType = self.info[0]
        self.status = "Connected"

    def device_setup(self):
        # Setup and call eWriteNames for AIN0 (all devices) and digital I/O (T4 only)
        # configuration.
        if self.deviceType == ljm.constants.dtT4:
            # LabJack T4 configuration

            # Set FIO5 (DIO5) and FIO6 (DIO6) lines to digital I/O.
            #     DIO_INHIBIT = 0xF9F, b111110011111.
            #                   Update only DIO5 and DIO6.
            #     DIO_ANALOG_ENABLE = 0x000, b000000000000.
            #                         Set DIO5 and DIO6 to digital I/O (b0).
            aNames = ["DIO_INHIBIT", "DIO_ANALOG_ENABLE"]
            aValues = [0xF9F, 0x000]
            numFrames = len(aNames)
            ljm.eWriteNames(self.handle, numFrames, aNames, aValues)

            # AIN0:
            #     The T4 only has single-ended analog inputs.
            #     The range of AIN0-AIN3 is +/-10 V.
            #     The range of AIN4-AIN11 is 0-2.5 V.
            #     Resolution index = 0 (default)
            #     Settling = 0 (auto)
            aNames = ["AIN0_RESOLUTION_INDEX", "AIN0_SETTLING_US"]
            aValues = [0, 0]
        #else:
        if True:
            # LabJack T7 and T8 configuration

            # AINO:
            #     Range = +/- 10 V
            #     Resolution index = 0 (default)
            aNames = ["AIN0_RANGE", "AIN0_RESOLUTION_INDEX"]
            #aValues = [10, 0]
            aValues = [10, 0]
            aNames = ["AIN1_RANGE", "AIN1_RESOLUTION_INDEX"]
            #aValues = [10, 0]
            aValues = [10, 0]
            
            # Negative channel and settling configurations do not apply to the T8
            #if self.deviceType == ljm.constants.dtT7:
            if True:
                #     Negative Channel = 199 (Single-ended)
                #     Settling = 0 (auto)
                
                if self.singleEnded:
                #single ended
                    aNames.extend(["AIN0_NEGATIVE_CH", "AIN0_SETTLING_US"])
                    aValues.extend([199, 0])
                    aNames.extend(["AIN1_NEGATIVE_CH", "AIN1_SETTLING_US"])
                    aValues.extend([199, 0])
                
                #differential

                if not self.singleEnded:
                    aNames.extend(["AIN0_NEGATIVE_CH", "AIN0_SETTLING_US"])
                    aValues.extend([1, 0])
                    aNames.extend(["AIN1_NEGATIVE_CH", "AIN1_SETTLING_US"])
                    aValues.extend([1, 0])
                

        numFrames = len(aNames)
        ljm.eWriteNames(self.handle, numFrames, aNames, aValues)

        print("\nSet configuration:")
        for i in range(numFrames):
            print("    %s : %f" % (aNames[i], aValues[i]))
        self.status = "Reading"
        
    def read_loop(self, logger = None, delay = 0.01):
        #attach logger
        self.runner = True
        print("\nStarting %s read loops.%s\n" % (str(self.loopAmount), self.loopMessage))
        i = 0
        intervalHandle = 1
        intervalValue = int(1000000 * delay)  # 2000000 microseconds = 1 seconds
        ljm.startInterval(intervalHandle, intervalValue)
        firstRun = True
        while self.runner:
            if firstRun:
                firstRun = False
                firstRunTime = ljm.getHostTick()
            try:
                
                # Setup and call eWriteNames to write to DAC0, and FIO5 (T4) or
                # FIO1 (T7 and T8).
                # DAC0 will cycle ~0.0 to ~5.0 volts in 1.0 volt increments.
                # FIO5/FIO1 will toggle output high (1) and low (0) states.
                #if self.deviceType == ljm.constants.dtT4:
                    #aNames = ["FIO5"]
                if True:
                    aNames = ["FIO1"]
                
                aValues = [self.fioState]
                numFrames = len(aNames)
                ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
                print("\neWriteNames : " +
                    "".join(["%s = %f, " % (aNames[j], aValues[j]) for j in range(numFrames)]))

                # Setup and call eReadNames to read AIN0 and FIO6 (T4) for
                # FIO2 (T7 and T8).
                #if self.deviceType == ljm.constants.dtT4:
                    #aNames = ["AIN0", "FIO6"]
                if True:
                    aNames = ["AIN0", "AIN1"]
                numFrames = len(aNames)
                time0 = ljm.getHostTick()
                aValues = ljm.eReadNames(self.handle, numFrames, aNames)
                time1 = ljm.getHostTick()
                read_run_time = time1 - time0
                relative_time = time1 - firstRunTime
                #pressurePSI = aValues[0] + 10
                if self.singleEnded:
                    Vr = aValues[0] - aValues[1]
                    pressurePSI = Vr  #here we are reading the difference between two analog inputs, Voltage Reading as a whole, modify this line to the equation you need based on whatever PT you are using and whatever formula you need

                if not self.singleEnded:
                    pressurePSI = aValues[0]
                
                #print("LJM_eReadName took %lld microseconds.\n", read_run_time)
                print("eReadNames  : " +
                    "".join(["%s = %f, " % (aNames[j], aValues[j]) for j in range(numFrames)]))
                self.status = "Reading"
                if logger is not None:
                    logger.log_add(relative_time, time1, aValues[0], aValues[1], self.fioState, pressurePSI)
                # Repeat every 200 milli seconds
                skippedIntervals = ljm.waitForNextInterval(intervalHandle)
                if skippedIntervals > 0:
                    print("\nSkippedIntervals: %s" % skippedIntervals)

                i += 1
                if self.loopAmount != "infinite":
                    if i >= self.loopAmount:
                        break
            except KeyboardInterrupt:
                break
            except Exception:
                import sys
                print(sys.exc_info()[1])
                self.runner = False
                self.status = sys.exc_info()[1]
                break
            

    def device_close(self):
        # Close interval and device handles
        self.runner = False
        ljm.cleanInterval(self.intervalHandle)
        ljm.close(self.handle)
        self.status = "Disconnected"
        

#test

if __name__ == "__main__":
    device = LMJdevice()
    logger = LMJlogger(['time_elapsed', 'A0', 'A1', 'Relay_Val'])
    device.read_loop(logger)
    device.device_close()

