#!/bin/bash

if [ $(uname -s) == Darwin ]; then
  EXT_DIR=$HOME"/Library/Application Support/Google/Chrome/Default/Extensions/ooelecakcjobkpmbdnflfneaalbhejmk/"
else
  EXT_DIR=$HOME"/.config/google-chrome/Default/Extensions/ooelecakcjobkpmbdnflfneaalbhejmk/"
fi

SCRIPT_DIR=$(ls -d "$EXT_DIR"* 2> /dev/null | tail -1)
if [ -z "$SCRIPT_DIR" ]
then
  echo SCRIPT_DIR not found, please install nutty extension >&2
  exit 1
fi

NUTTYSCRIPT="$SCRIPT_DIR""/nutty.py"


if [ -z "$NUTTYSCRIPT" ]
then
  echo $SCRIPT_DIR"/nutty.py" not found, please install nutty extension >&2
  exit 1
fi
chmod +x "$NUTTYSCRIPT" "$SCRIPT_DIR"/tmux*
exec "$NUTTYSCRIPT"


