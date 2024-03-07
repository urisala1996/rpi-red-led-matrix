#!/bin/bash

. /home/dietpi/rpi-red-led-matrix/bindings/python/samples/venv-matrix-artnet/bin/activate
sudo python3 /home/dietpi/rpi-red-led-matrix/bindings/python/samples/artnet-node.py &
sudo python3 /home/dietpi/rpi-red-led-matrix/bindings/python/samples/matrix-panel-receiver.py &

