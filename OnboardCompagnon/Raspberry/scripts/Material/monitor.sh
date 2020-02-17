#!/bin/bash

tail -F /var/log/syslog | grep --line-buffered 'g_mass_storage gadget: high-speed config' | while read;do kill `ps -ef | grep gst-launch-1.0 | grep filesink | awk '{print $2}'`;done
