#!/usr/bin/env python
from samplebase import SampleBase
import time

class SimpleSquare(SampleBase):
    def __init__(self, *args, **kwargs):
        super(SimpleSquare, self).__init__(*args, **kwargs)

    def run(self):
        offset_canvas = self.matrix.CreateFrameCanvas()
        print("TOTAL DIMENSIONS: {}x{}".format(offset_canvas.width,offset_canvas.height))
        total_cols = offset_canvas.width
        idx_col = 0
        while True:
            offset_canvas.Clear()
            for x in range(0,offset_canvas.height):
               offset_canvas.SetPixel(idx_col,x,255,0,0)
            idx_col = idx_col + 1
            if (idx_col >= total_cols):
               idx_col = 0
            time.sleep(1)
            #for x in range(0, offset_canvas.width):
            #    for y in range(0,offset_canvas.height):
            #        offset_canvas.SetPixel(x, y, 255, 0, 0)
            #offset_canvas.SetPixel(0,0,255,0,0)
            #offset_canvas.SetPixel(offset_canvas.height-1,0,255,0,0)
            #offset_canvas.SetPixel(offset_canvas.height-1,offset_canvas.width-1,255,0,0)
            #offset_canvas.SetPixel(0,offset_canvas.width-1,255,0,0)
            offset_canvas = self.matrix.SwapOnVSync(offset_canvas)


# Main function
if __name__ == "__main__":
    simple_square = SimpleSquare()
    if (not simple_square.process()):
        simple_square.print_help()
