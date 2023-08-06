#!/bin/bash

FIX_USER=$1
FIX_UID=$2

id $FIX_USER && CMD=usermod || CMD=useradd
echo $CMD -d /sbgenomics -o -u $FIX_UID $FIX_USER
$CMD -d /sbgenomics -o -u $FIX_UID $FIX_USER
