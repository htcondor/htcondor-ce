#!/bin/bash

# "timestamp=1544614059" "userDN=/C=UK/O=eScience/OU=Liverpool/L=CSD/CN=stephen jones" "userFQAN=/dteam/Role=NULL/Capability=NULL" "ceID=hepgrid6.ph.liv.ac.uk:9619/hepgrid6.ph.liv.ac.uk-condor" "jobID=1.0_hepgrid6.ph.liv.ac.uk" "lrmsID=1_hepgrid6.ph.liv.ac.uk" "localUser=dteam001"

convertEpochToTextDate()
{
  while read line; do

    regex="(.*timestamp=)([0-9][0-9]*)(.*)"
    if [[ $line =~ $regex ]]
    then
      leading="${BASH_REMATCH[1]}"
      epoch="${BASH_REMATCH[2]}"
      trailing="${BASH_REMATCH[3]}"
      textdate=$(date -u +"%Y-%m-%d %H:%M:%S" -d@$epoch)
      echo "${leading}${textdate}${trailing}"
    else
      echo $line
    fi
  done;
}

today=$(date -u --date='00:00:00 today' +%s)
yesterday=$(date -u --date='00:00:00 yesterday' +%s)
output=blah-$(date -u --date='yesterday' +%Y%m%d )-$(hostname -s)
CONST="EnteredCurrentStatus >= $yesterday && EnteredCurrentStatus < $today && RemoteWallclockTime !=0"

/usr/bin/condor_history -const "$CONST" \
 -format "\"timestamp=%d\" " EnteredCurrentStatus  \
 -format "\"userDN=%s\" " x509userproxysubject \
 -format "\"userFQAN=%s\" " x509UserProxyFirstFQAN \
 -format "\"ceID=hepgrid6.ph.liv.ac.uk:9619/hepgrid6.ph.liv.ac.uk-condor\" " EMPTY \
 -format "\"jobID=%v_hepgrid6.ph.liv.ac.uk\" " RoutedFromJobId \
 -format "\"lrmsID=%v_hepgrid6.ph.liv.ac.uk\" " ClusterId \
 -format "\"localUser=%s\"\n"  Owner  | convertEpochToTextDate \
   > /var/lib/condor/accounting/$output

