#!/bin/bash

nmcli con delete TEST-AP
nmcli con add type wifi ifname wlan0 mode ap con-name TEST-AP ssid artnet-config autoconnect false
nmcli con modify TEST-AP wifi.band bg
nmcli con modify TEST-AP wifi.channel 3
nmcli con modify TEST-AP wifi.cloned-mac-address 00:12:34:56:78:9a
nmcli con modify TEST-AP wifi-sec.key-mgmt wpa-psk
#nmcli con modify TEST-AP wifi-sec.proto rsn
#nmcli con modify TEST-AP wifi-sec.group ccmp
#nmcli con modify TEST-AP wifi-sec.pairwise ccmp
nmcli con modify TEST-AP wifi-sec.psk "admin"
nmcli con modify TEST-AP ipv4.method shared ipv4.address 192.168.4.1/24
nmcli con modify TEST-AP ipv6.method disabled
nmcli con up TEST-AP
