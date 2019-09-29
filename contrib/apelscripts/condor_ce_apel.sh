#!/bin/sh
# sjones@hep.ph.liv.ac.uk, 2019
# Run the processes of an HTCondor-CE + HTCondor accounting run

/usr/share/condor-ce/condor_blah.sh       # Make the blah file (CE/Security data)
/usr/share/condor-ce/condor_batch.sh      # Make the batch file (batch system job run times)
/usr/bin/apelparser                       # Read the blah and batch files in
/usr/bin/apelclient                       # Join blah and batch records to make job records
/usr/bin/ssmsend                          # Send job records into APEL system
