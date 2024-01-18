from multiprocessing.connection import Listener
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from operator import itemgetter


class TCPMatrixDisplay(object):

    # RGBMatrix Panel Variables
    ROWS_PANEL = 16
    COLS_PANEL = 32
    NUM_PANEL = 6
    PARALLEL = 1
    BRIGHTNESS = 100

    # Full display Variables
    DISPLAY_SIZE_X = 32*3
    DISPLAY_SIZE_Y = 16*2

    ARTNET_NODE_ADDR = ('127.0.0.1',6000)

    def __init__(self):
        self.options = self.rgbmatrix_options()
        self.display = RGBMatrix(options=self.options)
        self.canvas  = self.display.CreateFrameCanvas()

    ### RGBMatrixSetting
    def rgbmatrix_options(self):
        options = RGBMatrixOptions()
        options.multiplexing = 18
        options.row_address_type = 0
        options.brightness = self.BRIGHTNESS
        options.rows = self.ROWS_PANEL
        options.cols = self.COLS_PANEL
        options.chain_length = self.NUM_PANEL
        options.parallel = self.PARALLEL
        options.hardware_mapping = 'adafruit-hat'
        options.inverse_colors = True
        options.gpio_slowdown = 3
        options.pwm_lsb_nanoseconds = 100
        options.show_refresh_rate = 0
        options.disable_hardware_pulsing = False
        options.scan_mode = 1
        options.pwm_bits = 11
        options.pwm_dither_bits = 1
        options.daemon = 0
        options.drop_privileges = 0
        options.pixel_mapper_config = 'U-mapper'
        return options

    def showDisplay(self, datastream, data_len=None):
        idx = 0
        x = 0
        y = 0
        try:
            while ((y < (self.DISPLAY_SIZE_Y))):
                if (datastream[idx] is not None):
                    r = datastream[idx]
                    self.canvas.SetPixel(x, y, r, 0, 0)
                x += 1
                idx += 1
                if (x > (self.DISPLAY_SIZE_X - 1)):
                    x = 0
                    y += 1

            self.canvas = self.display.SwapOnVSync(self.canvas)
        except (IndexError):
            print("ERROR! IDX: {} DataLen: {}".format(idx,data_len))

    def run_receiver(self):

        listener = Listener(self.ARTNET_NODE_ADDR,authkey=b'dietpi')
        node_conn = listener.accept()
        print("Connection accepted from: {}".format(listener.last_accepted))

        while True:
            rx_data = node_conn.recv()
            if (rx_data is not None):
                #print(rx_data)
                matrix_data = list(rx_data)
                self.showDisplay(matrix_data,data_len=len(matrix_data))

            if rx_data == 'close':
                node_conn.close()
                break

        listener.close()

# Main function
if __name__ == "__main__":
    print("Receiver Process for uncompressed Pixel Data")
    matrixController = TCPMatrixDisplay()
    matrixController.run_receiver()
