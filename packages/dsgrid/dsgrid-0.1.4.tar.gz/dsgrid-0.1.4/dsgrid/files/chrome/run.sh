#!/bin/bash
set -e
su chrome <<'EOF'
Xvfb :21 -screen 0 1024x768x24 > /dev/null 2>&1 &
export HOST_IP=$(ip addr show dev eth0 | grep "inet " | awk '{print $2}' | cut -d '/' -f 1)
export DISPLAY=:21
java -jar selenium-server-standalone-2.39.0.jar -role webdriver -host ${HOST_IP} -hub http://${GRID_IP}:4444/grid/register -browser browserName=chrome
EOF
