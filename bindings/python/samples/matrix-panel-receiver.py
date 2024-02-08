from multiprocessing.connection import Listener
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from operator import itemgetter
import json

class TCPMatrixDisplay(object):

    def __init__(self,config):
        
        self.config = config
        
        self.num_panels = self.config['general-settings']['num_panels_width'] * self.config['general-settings']['num_panels_height']
        self.display_size_x = self.config['general-settings']['num_panels_width'] * self.config['matrix-settings']['panel_w']
        self.display_size_y = self.config['general-settings']['num_panels_height'] * self.config['matrix-settings']['panel_h']
        self.options = self.rgbmatrix_options()
        self.display = RGBMatrix(options=self.options)
        self.canvas  = self.display.CreateFrameCanvas()

    ### RGBMatrixSetting
    def rgbmatrix_options(self):
        options = RGBMatrixOptions()
        options.multiplexing = 18
        options.row_address_type = 0
        options.brightness = self.config['matrix-settings']['brightness']
        options.rows = self.config['matrix-settings']['panel_h']
        options.cols = self.config['matrix-settings']['panel_w']
        options.chain_length = self.num_panels
        options.parallel = 1
        options.hardware_mapping = 'adafruit-hat'
        options.inverse_colors = True
        options.gpio_slowdown = self.config['matrix-settings']['gpio_slowdown']
        options.pwm_lsb_nanoseconds = self.config['matrix-settings']['pwm_lsb_nanoseconds']
        options.show_refresh_rate = 0
        options.disable_hardware_pulsing = False
        options.scan_mode = 1
        options.pwm_bits = self.config['matrix-settings']['pwm_bits']
        options.pwm_dither_bits = self.config['matrix-settings']['pwm_dither_bits']
        options.daemon = 0
        options.drop_privileges = 0
        options.pixel_mapper_config = 'U-mapper'
        return options

    def showDisplay(self, datastream, data_len=None):
        idx = 0
        x = 0
        y = 0
        try:
            while ((y < (self.display_size_y))):
                if (datastream[idx] is not None):
                    r = datastream[idx]
                    self.canvas.SetPixel(x, y, r, 0, 0)
                x += 1
                idx += 1
                if (x > (self.display_size_x - 1)):
                    x = 0
                    y += 1

            self.canvas = self.display.SwapOnVSync(self.canvas)
        except (IndexError):
            print("ERROR! IDX: {} DataLen: {}".format(idx,data_len))

    def receive_data(self,socket):
        rx_len = self.display_size_x * self.display_size_y
        try:
            while True:
                rx_data = socket.recv()
                if (rx_data is not None):
                    #print(rx_data)
                    matrix_data = list(rx_data)
                    self.showDisplay(matrix_data,data_len=len(matrix_data))

                if rx_data == 'close':
                    socket.close()
                    break
        except EOFError:
            print("[MatrixController] EOF Error")
        except Exception as e:
            print("[MatrixController] Fatal error occurred: {}".format(e))
        finally:
            socket.close()
            print("[MatrixController] Socket closed")

# Main function
if __name__ == "__main__":

    print("--- Starting Process: Socket to Pixel Data")

    with open('fixture-config.json') as f:
        config = json.load(f)

    ARTNET_NODE_ADDR = (config['artnet-settings']['socket-ip'],config['artnet-settings']['socket-port'])
    matrixController = TCPMatrixDisplay(config)

    try:
        listener = Listener(ARTNET_NODE_ADDR,authkey=b'dietpi')
        node_sckt = listener.accept()
        print("Connection accepted from: {}".format(listener.last_accepted))

        matrixController.receive_data(node_sckt)

    except KeyboardInterrupt:
        print("\nRequest to terminate by the user")
    except Exception as e:
        print("Fatal error occurred: {}".format(e))
    finally:
        print("Connection closed")
        listener.close()
