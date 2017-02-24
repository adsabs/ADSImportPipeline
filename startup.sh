#!/bin/bash
#
# Runs the pipeline in the foreground so we can
# monitor it from supervisord
# AA 11/9/16

set -eu

script=$(readlink -f $0)
dirpath=$(dirname $script)
command="$dirpath/pipeline/ADSimportpipeline.py"
# must match what is in pipeline/psettings.py
pidfile="/tmp/ADSimportpipeline.lock"
python="/proj/adsx/python/bin/python"

# Proxy signals
function kill_app(){
    #kill $(cat $pidfile)
    $python $command stop
    sleep 3
    exit 0 # exit okay
}
trap "kill_app" SIGINT SIGTERM

# Launch daemon
$python $command start
sleep 3

# Loop while the pidfile and the process exist
while [ -f $pidfile ] && kill -0 $(cat $pidfile) ; do
    sleep 1
done

exit 234 # exit unexpected
