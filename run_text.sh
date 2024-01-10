#!/bin/bash
sudo utils/text-scroller -f $1 "ONIRIC" -C 255,0,0 --led-chain=2 --led-cols=32 --led-rows=16 --led-multiplexing=18 --led-row-addr-type=0 --led-gpio-mapping=adafruit-hat --led-pwm-dither-bits=1 --led-slowdown-gpio=4 --led-inverse --led-brightness=100
