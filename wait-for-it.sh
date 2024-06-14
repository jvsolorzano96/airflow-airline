#!/usr/bin/env bash
# Use this script to test if a given TCP host/port are available

WAITFORIT_cmdname=${0##*/}
WAITFORIT_host=
WAITFORIT_port=
WAITFORIT_timeout=15
WAITFORIT_interval=1
WAITFORIT_waitretry=0
WAITFORIT_curl=false

usage()
{
    exitcode="$1"
    cat << USAGE >&2
Usage:
    $WAITFORIT_cmdname host:port [-s] [-t timeout] [-- command args]
    -h HOST | --host=HOST       Host or IP under test
    -p PORT | --port=PORT       TCP port under test
                                Alternatively, you specify the host and port as host:port
    -s | --strict               Only execute subcommand if the test succeeds
    -t TIMEOUT | --timeout=TIMEOUT
                                Timeout in seconds, zero for no timeout
    -- COMMAND ARGS             Execute command with args after the test finishes
USAGE
    exit "$exitcode"
}

wait_for()
{
    if [ "$WAITFORIT_curl" = true ]; then
        echo "waiting for $WAITFORIT_host:$WAITFORIT_port"
        while ! curl http://$WAITFORIT_host:$WAITFORIT_port -m 2 -s --fail; do
            echo "waiting..."
            sleep $WAITFORIT_interval
        done
    else
        echo "waiting for $WAITFORIT_host:$WAITFORIT_port"
        while ! nc -z $WAITFORIT_host $WAITFORIT_port; do
            echo "waiting..."
            sleep $WAITFORIT_interval
        done
    fi
    echo "$WAITFORIT_host:$WAITFORIT_port is available"
}

wait_for_wrapper()
{
    timeout=$WAITFORIT_timeout

    if ! wait_for; then
        echo "timeout occurred after waiting $timeout seconds for $WAITFORIT_host:$WAITFORIT_port"
        exit 1
    fi
    if [ -n "$WAITFORIT_subcommand" ]; then
        echo "executing command: ${WAITFORIT_subcommand[*]}"
        exec "${WAITFORIT_subcommand[@]}"
    else
        exit 0
    fi
}

if [ "$#" -eq 0 ]; then
    usage 1
fi

while [ "$#" -gt 0 ]; do
    case "$1" in
        *:* )
        WAITFORIT_host=$(echo $1 | cut -d : -f 1)
        WAITFORIT_port=$(echo $1 | cut -d : -f 2)
        shift 1
        ;;
        -h | --host )
        WAITFORIT_host="$2"
        if [ "$WAITFORIT_host" = "" ]; then break; fi
        shift 2
        ;;
        -p | --port )
        WAITFORIT_port="$2"
        if [ "$WAITFORIT_port" = "" ]; then break; fi
        shift 2
        ;;
        -s | --strict )
        WAITFORIT_strict=1
        shift 1
        ;;
        -t | --timeout)
        WAITFORIT_timeout="$2"
        if [ "$WAITFORIT_timeout" = "" ]; then break; fi
        shift 2
        ;;
        --interval)
        WAITFORIT_interval="$2"
        if [ "$WAITFORIT_interval" = "" ]; then break; fi
        shift 2
        ;;
        --waitretry)
        WAITFORIT_waitretry="$2"
        if [ "$WAITFORIT_waitretry" = "" ]; then break; fi
        shift 2
        ;;
        --curl)
        WAITFORIT_curl=true
        shift 1
        ;;
        -- )
        shift
        WAITFORIT_subcommand=("$@")
        break
        ;;
        -*)
        echo "unknown option: $1"
        usage 1
        ;;
        * )
        usage 1
        ;;
    esac
done

if [ "$WAITFORIT_host" = "" ] || [ "$WAITFORIT_port" = "" ]; then
    echo "Error: you need to provide a host and port to test."
    usage 2
fi

wait_for_wrapper
