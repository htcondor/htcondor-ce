#!/bin/bash
# accountingRun.sh
# sjones@hep.ph.liv.ac.uk, 2019
# Run the processes of a HTCondor accounting run

/usr/share/apel/condor_ce_blah.sh       # Make the blah file (CE/Security data)
/usr/share/apel/condor_ce_batch.sh      # Make the batch file (Job times)
/usr/bin/apelparser                # Read the blah and batch files in
/usr/bin/apelclient                # Join blah and batch records to make job records
/usr/bin/ssmsend                   # Send job records into APEL system

