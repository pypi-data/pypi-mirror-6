#!/bin/bash

# check if environment variable setup
if [ ! "$CONFIG" == "" ]; then
    echo "CONFIG found"
else
    echo "CONFIG environment variable is not defined."
    exit 1
fi

# import config file
if [ -f $CONFIG ]; then
    source $CONFIG
else
    echo "File $CONFIG does not exists."
    echo "Please provide a valid file (like found in /etc/trebuchet/*.conf)."
    FILES=`ls /etc/trebuchet/*.conf`
    for f in $FILES
    do
        echo "CONFIG=$f $0"
    done

    exit 1
fi

LOCAL_OVERRIDE=/etc/trebuchet/local_override

if [ -f $LOCAL_OVERRIDE ]; then
    source $LOCAL_OVERRIDE
fi


# clean up file
cd {{ app_code }}

# locale var (DO NOT CHANGE)
export LANG="${LOCALE}"
export LANGUAGE="${LOCALE}"
export LC_CTYPE="${LOCALE}"
export LC_NUMERIC="${LOCALE}"
export LC_TIME="${LOCALE}"
export LC_COLLATE="${LOCALE}"
export LC_MONETARY="${LOCALE}"
export LC_MESSAGES="${LOCALE}"
export LC_PAPER="${LOCALE}"
export LC_NAME="${LOCALE}"
export LC_ADDRESS="${LOCALE}"
export LC_TELEPHONE="${LOCALE}"
export LC_MEASUREMENT="${LOCALE}"
export LC_IDENTIFICATION="${LOCALE}"
export LC_ALL="${LOCALE}"

{% block command_body %}{% endblock %}
