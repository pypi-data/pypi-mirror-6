#!/bin/sh

# Enable this option if you're debugging the script
# itself.
# set -x

# Check for PYTHON_VERSION
if [ -n "${PYTHON_VERSION}" ]; then
PYTHON="python${PYTHON_VERSION}"
else
PYTHON=`which python`
fi;

FIND=/usr/bin/find

### Root dir
ROOTDIR=`cd -P -- "$(dirname -- "$0")/.." && pwd -P`
### Directory where internal libraries are found
LIBDIR="$ROOTDIR"
### Directory where scripts are found
BINDIR="$ROOTDIR/bin"

### Required for backward-compatibility
DJANGO_SETTINGS_MODULE='local_settings'

# Set DJANGO_HOME unless its already provided
if test -z "$DJANGO_HOME" ; then
 echo "WARNING: DJANGO_HOME not found, using default"
 export DJANGO_HOME="$ROOTDIR/contrib"
fi

PYTHONPATH="$ROOTDIR:$LIBDIR:$DJANGO_HOME"
export DJANGO_SETTINGS_MODULE PYTHONPATH ROOTDIR 
export SCHEVO_OPTIMIZE=1

clean() {
    # ensure that we start clean
    $FIND $ROOTDIR -name "*.py[co]" -exec rm -f '{}' ";" || true
    $FIND $ROOTDIR -name "*.sw[po]" -exec rm -f '{}' ";" || true
}
manage() {
    shift;
    $PYTHON $BINDIR/manage.py $@
}
#create_user() {
#    shift;
#    python $BINDIR/create_user.py $@
#}
runserver() {
    shift;
    $PYTHON $BINDIR/runserver.py $@
}
respawn(){
    shift;
    eval "$BINDIR/respawn.sh" "$@"
}
moinmoin_start(){
    shift;
    eval "$BINDIR/moinmoin.sh" "$@"
} 
comment_manager_start(){
    shift;
    eval "$PYTHON $BINDIR/CommentManager.py $@";
}
upgradedb(){
	shift;
	eval "$BINDIR/upgradedb.sh" "$@";
}
case $1 in manage)
    manage "$@"
    ;; 
clean)
    clean;
    ;;
respawn)
    clean;
    respawn "$@"
    ;;
runserver)
    clean; # start clean
    runserver "$@"
    ;;
moinmoin)
    clean;
	moinmoin_start "$@"
    ;;
manage_comments)
    clean;
    comment_manager_start "$@"
    ;;
upgradedb)
	upgradedb "$@"
	;;
*)
    #echo "Usage: debug.sh <clean|manage|respawn|runserver|moinmoin> [options]"
    echo "Usage: $0 <command> [options]"
    echo "Available commands: clean, manage, respawn, runserver, moinmoin,
	manage_comments, upgradedb"

    exit 0;
esac        
