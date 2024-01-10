#!/usr/bin/env python
import time
import board
import json
import os
from stupidArtnet import StupidArtnetServer
from samplebase import SampleBase

class LedMatrixArtnet(SampleBase):
    def __init__(self, width, height, *args, **kwargs):
        super(LedMatrixArtnet, self).__init__(*args, **kwargs)
        self.total_height = height
        self.total_width = width
        self.num_ch = 1

    def run(self):
        offset_canvas = self.matrix.CreateFrameCanvas()

        while True:
            data = server.get_buffer(listener_id=u1_listener)
            #data2 = server.get_buffer(listener_id=u2_listener)
            #if len(data2) > 0:
            #    print("Data for Universe 2")

            if len(data) > 0:
                #print(data)
                for row in range(self.total_height):
                    row_offset = row * (self.total_width * self.num_ch)
                    for col in range(self.total_width):
                        pixel_idx = row_offset + (col * self.num_ch)
                        offset_canvas.SetPixel(row,col,data[pixel_idx],0,0)

            offset_canvas = self.matrix.SwapOnVSync(offset_canvas)


# Main function
if __name__ == "__main__":

    dirname = os.path.dirname(__file__)
    data = json.load(open(os.path.join(dirname, 'fixture-config.json')))

    universe = data["settings"]["universe"]
    #universe2 = 2

    panel_width = data["settings"]["panel_width"]
    panel_height = data["settings"]["panel_height"]
    num_panels_width = data["settings"]["num_panels_width"]
    num_panels_height = data["settings"]["num_panels_height"]

    num_panels = num_panels_height * num_panels_width
    pixelCount = panel_width*panel_height * num_panels

    print("ARTNET - RGB MATRIX Controller")
    print("Total Fixture dimensions: {}x{} pixels".format(num_panels_width*panel_width, num_panels_height*panel_height))
    print("Panel dimensions: {}x{} pixels".format(panel_width,panel_height))
    print("Number of panels: {}x{} panels".format(num_panels_width,num_panels_height))
    print("Universe: {}".format(universe))
    #universe = 1
    server = StupidArtnetServer()

    u1_listener = server.register_listener(universe)
    #u2_listener = server.register_listener(universe2)

    matrix = LedMatrixArtnet(panel_width,panel_height)

    if (not matrix.process()):
        del server
        matrix.print_help()

