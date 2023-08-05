#!/usr/bin/env sh

# Refresh Google Chrome using AppleScript when a tab's URL contains the
# string specified.

osascript <<EOS
tell application "Google Chrome"
    repeat with w in windows
        repeat with t in w's tabs
            if t's URL contains "oraide/docs/_build" then
                reload t
            end if
        end repeat
    end repeat
end tell
EOS
