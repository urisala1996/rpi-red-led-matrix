# Art-Net protocol for rpi-rgb-led-matrix
# https://github.com/hzeller/rpi-rgb-led-matrix
# License: MIT
from twisted.internet import protocol, endpoints
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from struct import pack, unpack
from PIL import Image
from PIL import ImageDraw
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from operator import itemgetter
from collections import deque
from array import array


### Variables
# RGBMatrix Panel Variables

number_of_rows_per_panel = 16
number_of_columns_per_panel = 32
number_of_panels = 4
parallel = 1

# Art-Net Variables

display_size_x = 32*4
display_size_y = 16
universum_start = 0
universum_count = 26
channel_per_univers = 510

# FrameBuffer

frameBuffer = None
frameBufferCounter = 0
rgbframeLength = 0
#Number of sequences to store in buffer
seqBufferSize = 16 # Min 4 Buffer
seqBufferOffset = 1 #2
lastSequence = 0

frameArray = [[0, 0, 0, [0]]]


### RGBMatrixSetting

def rgbmatrix_options():
  options = RGBMatrixOptions()
  options.multiplexing = 18
  options.row_address_type = 0
  options.brightness = 40
  options.rows = number_of_rows_per_panel
  options.cols = number_of_columns_per_panel
  options.chain_length = number_of_panels
  options.parallel = parallel
  options.hardware_mapping = 'adafruit-hat'
  options.inverse_colors = True
  #options.led_rgb_sequence = "RGB"
  options.gpio_slowdown = 4
  #options.pwm_lsb_nanoseconds = 150
  options.show_refresh_rate = 1
  options.disable_hardware_pulsing = False
  #options.scan_mode = 0
  options.pwm_bits = 11
  options.daemon = 0
  options.drop_privileges = 0
  return options;

options = rgbmatrix_options()
display = RGBMatrix(options=options)
canvas  = display.CreateFrameCanvas()

class ArtNet(DatagramProtocol):

    def addToFrameBufferArray(self, sequence, universe, rgb_length, data):
        global frameArray
        if (sequence > 0):
#           The sequence number is read from the array
            frameSequenceInt = int(float(str(frameArray [0][0])))
#           If the sequence number is 0, the initial array string has been recognised
#           After filling it, the initial array must be removed
            if (frameSequenceInt == 0):
                frameArray.append([sequence, universe, rgb_length, data])
                frameArray.pop(0)
            else:
                frameArray.append([sequence, universe, rgb_length, data])

    def cleanUpFrameBuffer(self, sequenceNr):
        global frameArray
        bufferCounter = 0
        bufferSize = seqBufferSize * universum_count
        while(bufferCounter < bufferSize):
            if (bufferCounter < len(frameArray)):
                if (sequenceNr >= int(float(str(frameArray [bufferCounter][0])))):
                    frameArray.pop(bufferCounter)
            bufferCounter += 1

#   This function returns an entire sequence also all universe pulled together into an array
    def getSequenceFromFrameBuffer(self, sequenceNr):
        global frameArray
        finalFrameArray = []
        rgbframeLength = 0
#       Sequence correction because there can only be sequences between 1 and 255
        if (sequenceNr == -1 or sequenceNr == 0):
            sequenceNr = sequenceNr + 255
        if (sequenceNr > 0):
#           Sort the array by sequence
#           frameArray = sorted(frameArray, key=lambda x: x[1])
            frameArray = sorted(frameArray,key=itemgetter(1))
            bufferCounter = 0
#           frameCounter counts the data packets (universe packets) in a sequence
#           If a data packet is lost, the entire sequence is discarded.
            frameCounter = 0
            bufferSize = seqBufferSize * universum_count
            while(bufferCounter < bufferSize):
                if (bufferCounter < len(frameArray)):
                    if (sequenceNr == int(float(str(frameArray [bufferCounter][0])))):
                        if (frameCounter == int(float(str(frameArray [bufferCounter][1])))):
                            frameCounter += 1
                        else:
                            self.cleanUpFrameBuffer(sequenceNr)
#                           If data is missing from the FrameBuffer, an empty buffer is returned
                            finalFrameArray = []
                            return (finalFrameArray, 0)
                        finalFrameArray = finalFrameArray + frameArray [bufferCounter][3]
                        rgbframeLength = rgbframeLength + int(float(str(frameArray [bufferCounter][2])))
                        frameArray.pop(bufferCounter)
                bufferCounter += 1
                if (len(frameArray) > bufferSize):
                    frameArray = [[0, 0, 0, [0]]]
            return (finalFrameArray, rgbframeLength)

    def datagramReceived(self, data, addr):
        global lastSequence
        #print("Packet Length: {}".format(len(data)))
        #print("Packet From: {}".format(data[0:8]))
        if ((len(data) > 18) and (data[0:8] == b'Art-Net\x00')):
            rawbytes = list(data) #map(ord, data)
            opcode = rawbytes[8] + (rawbytes[9] << 8)
            protocolVersion = (rawbytes[10] << 8) + rawbytes[11]
            #print("OpCode: {} Version: {}".format(opcode,protocolVersion))
            if ((opcode == 0x5000) and (protocolVersion >= 14)):
                sequence = rawbytes[12]
                physical = rawbytes[13]
                sub_net = (rawbytes[14] & 0xF0) >> 4
                universe = rawbytes[14] & 0x0F
                net = rawbytes[15]
                rgb_length = (rawbytes[16] << 8) + rawbytes[17]
#               print("Sequence: {} Phy: {} SubNet: {} Universe: {} Net: {} RGB_Len: {}".format(sequence,physical,sub_net,universe,net,rgb_length))
                (sequence, physical, sub_net, universe, net, rgb_length)
                rgbdata = rawbytes[18:(rgb_length+18)]
#               self.addToFrameBufferArray(sequence,universe,rgb_length,rgbdata)
#               Subnet and universe in one variable, so 256 universes are possible
                self.addToFrameBufferArray(sequence,rawbytes[14],rgb_length,rgbdata)
                if(lastSequence != sequence):
                    frameBuffer, rgbframeLength = self.getSequenceFromFrameBuffer(sequence - seqBufferOffset)
                    if(len(frameBuffer)):
                       self.showDisplay(display_size_x,display_size_y,frameBuffer,rgbframeLength)
                lastSequence = sequence

    def showDisplay(self, display_size_x, display_size_y, datastream, rgb_length):
         global canvas
         idx = 0
         x = 0
         y = 0
         #print(datastream)
         while ((y < (display_size_y))):
             r = datastream[idx]
             canvas.SetPixel(x, y, r, 0, 0)
             x += 1
             idx += 1
             if (x > (display_size_x - 1)):
                 x = 0
                 y += 1

         canvas = display.SwapOnVSync(canvas)


reactor.listenUDP(6454, ArtNet())
reactor.run()
