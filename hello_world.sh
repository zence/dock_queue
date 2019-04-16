#! /bin/bash

a=$1
echo "Hello World!"
if [[ ${a} -lt 15 ]]; then
  sleep $((a*2+1))
else
  sleep $((30-a))
fi
