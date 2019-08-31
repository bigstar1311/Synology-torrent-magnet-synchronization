#!/bin/bash
export LANG=en_US.utf8
NowDate=$(date +%Y%m%d)-$(date +%H%M) 
cd /volume1/bigstar131/git_server/Synology-torrent-magnet-synchronization
git add *
git commit -m $NowDate
git push
