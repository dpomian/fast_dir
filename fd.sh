#!/bin/sh
res=`path/to/fd.py $@`
cmd=`echo $res | awk '{print $1;}'`

if [ "$cmd" = "cd" ]; then
    $res
else
    echo "$res"
fi