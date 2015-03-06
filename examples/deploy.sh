#!/bin/bash

# Example script to run commands in remote virtual machines

# NOTE: Remember to configure auto-identity file in ~/.ssh/config file
#       See: http://nerderati.com/2011/03/simplify-your-life-with-an-ssh-config-file/
#set -v
play dist
scp target/universal/ux-adchat-1.0-SNAPSHOT.zip ubuntu@54.235.223.72:~/
scp remote.sh ubuntu@54.235.223.72:~/
ssh -t -t ubuntu@54.235.223.72 <<DEPLOYSCRIPT
cd ~
chmod 740 remote.sh
./remote.sh
exit
DEPLOYSCRIPT
echo "Happy coding"
