#!/bin/sh
# inspector - queries host details then caches the result in the temp folder.

# Work dir
WD=${XDG_CACHE_HOME:-~/.cache}/pave
# Cache file name
CFN=$WD/platform.json

# check if cache file exists and > 0
if [ -r "$CFN" -a -s "$CFN" ]; then
# pass
    :
else
# create tempfolder if it doesn't exist.
    if [ ! -f "$WD" ]; then
        mkdir -p "$WD"
        chmod 0750 "$WD" > /dev/null 2>&1
    fi

# collect info from one of the files below.
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        ID=$NAME
        RL=$VERSION_ID
        set -- $VERSION
        CN="$2 $3"
        CN=${CN#"("}
        CN=${CN%")"}

    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        ID=$DISTRIB_ID
        RL=$DISTRIB_RELEASE
        CN=$DISTRIB_CODENAME

    elif [ -f /etc/debian_version ]; then
        ID=Debian
        RL=$(cat /etc/debian_version)
        CN=$(cat /etc/debian_version)

    elif [ -f /etc/fedora-release ]; then
        set -- $(cat /etc/fedora-release)
        ID=$1
        RL=$3
        CN="$4 $5"
        CN=${CN#"("}
        CN=${CN%")"}

    elif [ -f /etc/redhat-release ]; then
        ID=Redhat
        RL=$(cat /etc/redhat-release)
        CN=$(cat /etc/redhat-release)

    fi

# get locale
    enc=`expr $LANG : '.*\.\(.*\)'`
# use uname output as script params
    set -- $(uname -s -n -i)

    cat << EOF > "$CFN"
{"system":"$1","node":"$2","proc":"$3","linux_dist":["$ID","$RL","$CN"],
 "encoding":"$enc"}
EOF

fi

# print results file to stdout and exit
cat "$CFN"
