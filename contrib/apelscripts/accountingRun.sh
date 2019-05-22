#!/bin/bash
# accountingRun.sh
# sjones@hep.ph.liv.ac.uk, 2019
# Run the processes of a HTCondor-ce + HTCondor accounting run

/usr/bin/condor_ce_blah.sh         # Make the blah file (CE/Security data)
/usr/bin/condor_batch.sh           # Make the batch file (Job times)
/usr/bin/apelparser                # Read the blah and batch files in
/usr/bin/apelclient                # Join blah and batch records to make job records
/usr/bin/ssmsend                   # Send job records into APEL system

