#!/bin/sh

#if there is one argument which is "stop", then we kill libervia
DEBUG=""
if [ $# -eq 1 ];then
    if [ $1 = "stop" ];then
        echo "Terminating Libervia"
        pkill -f "twistd.*libervia"
        exit 0
    fi
    if [ $1 = "debug" ];then
        echo "Launching Libervia in debug mode"
        DEBUG="--debug"
    fi
fi

NAME='libervia'
PYTHON='python'

#We use python to parse config files
eval `"$PYTHON" << PYTHONEND
from ConfigParser import SafeConfigParser
from os.path import expanduser, join
import sys

config = SafeConfigParser(defaults={'local_dir':'~/.libervia',
                                    'pid_dir':'/tmp',
                                    'log_dir':'%(local_dir)s'})
try:
    config.read(map(expanduser, ['/etc/libervia.conf', '~/libervia.conf', '~/.libervia.conf', 'libervia.conf', '.libervia.conf']))
except:
    print ("echo \"/!\\ Can't read main config ! Please check the syntax\";")
    print ("exit 1")
    sys.exit()

env=[]
env.append("LOCAL_DIR='%s'" % join(expanduser(config.get('DEFAULT', 'local_dir')),''))
env.append("PID_DIR='%s'" % join(expanduser(config.get('DEFAULT', 'pid_dir')),''))
env.append("LOG_DIR='%s'" % join(expanduser(config.get('DEFAULT', 'pid_dir')),''))

print ";".join(env)
PYTHONEND
`

PID_FILE="$PID_DIR$NAME.pid"
LOG_FILE="$LOCAL_DIR$NAME.log"
DAEMON="n"
MAIN_OPTIONS="-${DAEMON}o"

#Don't change the next line
AUTO_OPTIONS=""
ADDITIONAL_OPTIONS="--pidfile $PID_FILE --logfile $LOG_FILE $AUTO_OPTIONS $DEBUG"

log_dir=`dirname "$LOG_FILE"`
if [ ! -d $log_dir ] ; then
    mkdir $log_dir
fi

echo "Starting Libervia..."
twistd $MAIN_OPTIONS $ADDITIONAL_OPTIONS $NAME
