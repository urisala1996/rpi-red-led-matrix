#!/bin/bash
ipaddr=$(ip a | grep inet | grep eth0 | grep -Po '\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b\/\d{1,2}')
echo $ipaddr