#!/bin/bash

help_message="./set_app_bound <application-name> <bound description | left top right bottom> "

if [[ $# -lt 2 ]]; then
    echo "Invalid number of input arguments."
    echo ""
    echo $help_message
    exit 1
fi

app="$1"
case $app in
    c)
    app="chrome"
    ;;

    s)
    app="safari"
    ;;

    p)
    app="preview"
    ;;

    f)
    app="finder"
    ;;

    t)
    app="terminal"
    ;;
esac

if [[ $# -eq 2 ]]; then
    bound_descr="$2"
    case $bound_descr in
        m2-full|m2|2f|2)
        bound="{1440, 23, 2520, 1920}"
        ;;

        m2-bottom-1-2|m2-bottom-half)
        bound="{1440, 981, 2520, 1920}"
        ;;

        m2-top-1-2|m2-top-half|m2-half)
        bound="{1440, 23, 2520, 977}"
        ;;

        m2-bottom-2-3)
        bound="{1440, 678, 2520, 1920}"
        ;;

        m2-top-1-3)
        bound="{1440, 23, 2520, 683}"
        ;;

        m2-top-2-3|m2-top|2t)
        bound="{1440, 23, 2520, 1245}"
        ;;

        m2-bottom-1-3|m2-bottom|2b)
        bound="{1440, 1250, 2520, 1920}"
        ;;

        full|f|1f|1)
        bound="{41, 23, 1437, 900}"
        ;;

        left-1-2|left-half|lh)
        bound="{41, 23, 733, 900}"
        ;;

        right-1-2|right-half|half|rh|h)
        bound="{736, 23, 1439, 900}"
        ;;

        right-2-3|right|r)
        bound="{470, 23, 1439, 900}"
        ;;

        left-2-3|left|l)
        bound="{41, 23, 1000, 900}"
        ;;

        *)
        echo "Invalid bound description, set full screen in main monitor"
        bound="{41, 23, 1437, 900}"
        ;;
    esac
else
    if [[ $# -ne 5 ]]; then
        echo "Invalid number of input arguments."
        echo ""
        echo $help_message
        exit 1
    fi

    bound="{$2, $3, $4, $5}"
fi

#echo "App: $app"
#echo "Bound: $bound"

# osascript -e "tell application \"Safari\" to set the bounds of the front window to {1479, 23, 2520, 1245}"
osascript <<EOF
tell application "$app"
    set the bounds of the front window to $bound
end tell
tell application "$app"
    activate
end tell
EOF

