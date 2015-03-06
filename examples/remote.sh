#! /bin/bash

# Example script to deploy a Play application in a Ubuntu Virtual Machine

set -e
set -v
#checking running server
JAVA_COUNT=`ps -ae | grep java | wc -l`
PID_FILE=/home/ubuntu/ux-adchat-1.0-SNAPSHOT/RUNNING_PID
echo "JAVA_COUNT="$JAVA_COUNT
if [ "$JAVA_COUNT" -gt 0 ]; then
	echo "A server instance is running. Stopping it"
	sudo start-stop-daemon --stop --pidfile=$PID_FILE
fi
#set home dir (where downloads are)
HOME_DIR=/home/ubuntu
echo "HOME_DIR="$HOME_DIR
cd $HOME_DIR
#delete previous folder
sudo rm -rf ux-adchat-1.0-SNAPSHOT
#unzip
unzip -q ux-adchat-1.0-SNAPSHOT.zip
#change to project dir
PROJECT_DIR=$HOME_DIR/ux-adchat-1.0-SNAPSHOT
echo "PROJECT_DIR="$PROJECT_DIR
cd $PROJECT_DIR
#run script
sudo start-stop-daemon --background --start --chuid root --exec $PROJECT_DIR/bin/ux-adchat -- -Dconfig.resource=application.prod.conf -Dhttp.port=80 -Dhttp.address=0.0.0.0
cat $PROJECT_DIR/logs/application.log
