#!/bin/bash

#Find the Process ID and kill it
PID=`ps -eaf | grep -w "python3 /home/dietpi/rpi-red-led-matrix/bindings/python/samples/matrix-panel-receiver.py" | grep -v grep | grep -v sudo| awk '{print $2}'`
if [[ "" !=  "$PID" ]]; then
  echo "killing $PID"
  sudo kill -9 $PID
fi

#Find the Process ID and kill it
PID=`ps -eaf | grep -w "python3 /home/dietpi/rpi-red-led-matrix/bindings/python/samples/artnet-node.py" | grep -v grep | grep -v sudo| awk '{print $2}'`
if [[ "" !=  "$PID" ]]; then
  echo "killing $PID"
  sudo kill -9 $PID
fi
