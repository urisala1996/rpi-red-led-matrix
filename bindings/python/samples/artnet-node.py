from twisted.internet import protocol, endpoints
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from struct import pack, unpack
from operator import itemgetter
from multiprocessing.connection import Client
import time
import json


# Art-Net Variables
NUM_UNIVERSES = 12

class ArtnetPacket:

    ARTNET_HEADER = b'Art-Net\x00'

    def __init__(self):
        self.op_code = None
        self.ver = None
        self.sequence = None
        self.physical = None
        self.universe = None
        self.real_universe = None
        self.length = None
        self.data = None

    def __str__(self):
        return ("ArtNet package:\n - op_code: {0}\n - version: {1}\n - "
                "sequence: {2}\n - physical: {3}\n - universe: {4}\n - "
                "length: {5}\n - data : {6}\n - ").format(
            self.op_code, self.ver, self.sequence, self.physical,
            self.universe, self.length, self.data)

    def unpack_artnet_packet(raw_udp_data):
        if unpack('!8s', raw_udp_data[:8])[0] != ArtnetPacket.ARTNET_HEADER:
            print("Received a non Art-Net packet")
            return None

        packet = ArtnetPacket()
        (packet.op_code, packet.ver, packet.sequence, packet.physical,
            packet.universe, packet.length) = unpack('!HHBBHH', raw_udp_data[8:18])

        packet.data = unpack(
            '{0}s'.format(int(packet.length)),
            raw_udp_data[18:18+int(packet.length)])[0]

        packet.universe = (packet.universe >> 8) & 0xF

        return packet

class FrameSequencer:
    def __init__(self, max_chunks):
        self.max_chunks = max_chunks
        self.buffer = bytearray()  # Assuming binary data, you can modify for other data types
        self.expected_sequence = 0
        self.buffer_len = 0
        self.is_ready = False

    def receive_chunk(self, data, data_len, sequence_number):

        self.is_ready = False

        if sequence_number == self.expected_sequence:
            # Append the data if the sequence number is as expected
            self.buffer += data
            self.expected_sequence += 1
            self.buffer_len += data_len

            if self.expected_sequence == self.max_chunks:
                #print("[CONCAT] Reached full sequence, length = {}".format(self.buffer_len))
                total_buf = self.buffer
                total_buf_len = self.buffer_len
                self.reset()
                self.is_ready = True
                return (True, total_buf_len, total_buf)

        elif sequence_number == 0:
            # If a new sequence is started, reset the buffer
            self.reset()

        else:
            # Discard out-of-order chunks
            print(f"[CONCAT] Received {sequence_number} instead of {self.expected_sequence}. Discarding.")

        return (self.is_ready, self.buffer_len, self.buffer)

    def reset(self):
        # Reset the concatenator state
        self.buffer = bytearray()
        self.expected_sequence = 0
        self.buffer_len = 0
        self.is_ready = False


class ArtNet(DatagramProtocol):

    def datagramReceived(self, data, addr):
        global DataFrameSequencer
        global matrix_conn

        if ((len(data) > 18)):
            rx_artnet_packet = ArtnetPacket.unpack_artnet_packet(data)
            #print(rx_artnet_packet)
            if ((rx_artnet_packet.op_code == 80) and (rx_artnet_packet.ver >= 14)):
                #print(rx_artnet_packet.universe)
                universe_data = bytearray(rx_artnet_packet.data)
                pixel_data_ready, pixel_data_len, pixel_data = DataFrameSequencer.receive_chunk(universe_data, rx_artnet_packet.length, rx_artnet_packet.universe)
                if (pixel_data_ready is True):
                    #Send Pixels to Matrix Controller
                    matrix_conn.send(pixel_data)


if __name__ == '__main__':

    with open('/home/dietpi/rpi-red-led-matrix/bindings/python/samples/fixture-config.json') as f:
        config = json.load(f)

    NUM_UNIVERSES = int(( int(config['general-settings']['num_panels_width']) * int(config['general-settings']['num_panels_height']) * int(config['matrix-settings']['panel_w']) * int(config['matrix-settings']['panel_h'])) / 512)

    ADDRESS = (config['artnet-settings']['socket-ip'],int(config['artnet-settings']['socket-port']))

    DataFrameSequencer = FrameSequencer(NUM_UNIVERSES)
    address = ('127.0.0.1', 6000)
    connection_retries = 10
    print("--- Starting Process from Artnet Data to RX Socket")
    print("--- Number of Universes: {}".format(NUM_UNIVERSES))

    while True:
        try:
            with Client(ADDRESS,authkey=b'dietpi') as matrix_conn:
                print("Connected to Socket-Matrix")
                connection_retries = 5
                reactor.listenUDP(6454,ArtNet())
                reactor.run()

            print("Connection closed")
            time.sleep(2)

        except ConnectionRefusedError:
            if (connection_retries):
                connection_retries -= 1
                print("Connection refused... retries: {}".format(connection_retries))
                time.sleep(3)
                continue
            else:
                print("No more retries! BYE")
                break

        except KeyboardInterrupt:
            #reactor.stop()
            #matrix_conn.close()
            print("Request to end Artnet Node")
            exit(0)
            break

        except BrokenPipeError:
            connection_retries = 0
            time.sleep(1)
            reactor.stop()
            break

        except Exception as e:
            print("Fatal Error occurred: {}".format(e))
            break

