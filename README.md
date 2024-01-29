HTCondor-CE
===========

[![Build and test HTCondor-CE RPMs](https://github.com/htcondor/htcondor-ce/actions/workflows/build_and_test_rpms.yml/badge.svg?branch=V5-branch)](https://github.com/htcondor/htcondor-ce/actions/workflows/build_and_test_rpms.yml)

---

A site grid gatekeeper technology based solely on HTCondor components.

This package is simply a thin set of wrappers around HTCondor, allowing you to
run a HTCondor-CE without disrupting a site HTCondor install.

For example, `condor_ce_q` is the HTCondor-CE equivalent to `condor_q` for the
HTCondor-CE processes.  This package took much of its inspiration - and base 
code - from OSGs condor-cron package.

Sites are encouraged to install the sub-package `htcondor-ce-condor` or
`htcondor-ce-pbs`, depending on which batch manager they run.

Download
--------

HTCondor-CE RPMs are available from the following locations:

- HTCondor Yum repositories: https://research.cs.wisc.edu/htcondor/yum/
- OSG Yum repositories: https://opensciencegrid.org/docs/common/yum/

Versioning
----------

At any given time, two versions of HTCondor-CE are maintained, a stable and a development version.
In this repository, the `master` branch contains the latest version of HTCondor-CE (i.e. development) while the `stable`
branch contains the previous version.

- [Development](https://htcondor-ce.readthedocs.io/en/latest/): HTCondor-CE 4
- [Stable](https://htcondor-ce.readthedocs.io/en/stable/): HTCondor-CE 3

Issues
------

Please share any issues or questions regarding the HTCondor-CE via the following mailing lists:
- [htcondor-users@cs.wisc.edu](mailto:htcondor-users@cs.wisc.edu): For issues and questions open to the community.
- [htcondor-admin@cs.wisc.edu](mailto:htcondor-admin@cs.wisc.edu): For issues and questions containing private information.
- [htcondor-security@cs.wisc.edu](mailto:htcondor-security@cs.wisc.edu): For issues regarding security problems/vunerabilities.
  For more information regarding reporting security problems go to [HTCSS Security](https://htcondor.org/security/).

Diagrams
--------

Below are diagrams to show the flow of a Job submitted to an HTCondor-CE to being executed in
a different batch system. ***Diagram A*** showcases an setup where the HTCondor-CE is located on the
same host as the destination batch system. While ***Diagram B*** showcases a setup with the HTCondor-CE
submitting a job to a remote batch system.

> Note: In both setups the HTCondor-CE ***Schedd*** sends Master and Schedd Ads to the ***Central Collector***

### HTCondor-CE workflow (Diagram A)
``` mermaid
flowchart LR

%% ID FORMAT:
%% - External nodes are numbered (0 - 100)
%% - Internal nodes are alphabetic (A - Z)
%% - Nodes within nested subgraphs are
%%   are labelled by double letters (AA - ZZ)
%% - All subgraph names are capitalized (Blahp)
%%   while nodes with the same name are lowercase (blahp)
subgraph HM[CE & Batch System Host Machine]
    subgraph HTCondor-CE
        %%direction LR %% Flowchart direction statement overrides statements in connected subgraphs; comment these out.
        A[[SchedD]] -- Original Job --> B(Job Router)
        B -- Routed Job --> A
        A -- Routed Job --> C{Grid Manager}
        %% Note: Used 1 to place Disk higher in ordering
        A -- </br>-Original Job Ad</br>-Routed Job Ad --> 1[(Disk)]
        subgraph Blahp
            %%direction LR
            %% Configure nested subgraphs above internal nodes
            subgraph lsf_*.sh
                direction LR %% Set direction of isolated subgraphs
                AA[submit] ---|OR| BB[cancel]
                BB ---|OR| CC[status]
            end
            E[[blahp]] --> lsf_*.sh
            F[common_sub</br>_attr.sh] -->|attrs| lsf_*.sh
            lsf_*.sh -->|args| F
        end
    end
    subgraph Batch System
        %%direction LR
        G((qsub))
    end
end
%% -- External Nodes --
0>Job Ad]
%% -- External Nodes --
%% -- Subgraph Links --
C <--> E
lsf_*.sh ---> G
0 --> A
%% Schedd connects to Global Central Collector
A == Ads ==> Z(((Central Collector)))
%% Stylize Outer host machine box
style HM fill:#FFF,stroke:#000
%% -- Subgraph Links --
```

### Bosco Cluster workflow (Diagram B)

In this setup where the HTCondor-CE submits to a remote batch system, incoming jobs
are required to specify ***grid_resource = \<batch\> \<system\> \<hostname\>***.

> Note: The ***Blaph*** on the remote host works exactly the same as in Diagram A
> except that the ***Grid Manager*** communicates over SSH.

```mermaid
flowchart LR

%% ID FORMAT:
%% - External nodes are numbered (0 - 100)
%% - Internal nodes are alphabetic (A - Z)
%% - Nodes within nested subgraphs are
%%   are labelled by double letters (AA - ZZ)
%% - All subgraph names are capitalized (Blahp)
%%   while nodes with the same name are lowercase (blahp)
subgraph HM1[CE Host Machine]
    subgraph Bosco Cluster
        %%direction LR %% Flowchart direciton statement overrides statements in connected subgraphs; comment these out
        A[[SchedD]] -- Original Job --> Z(Job Router)
        Z -- Routed Job --> A
        A -- Routed Job --> B{Grid</br>Manager}
        B --- D[ssh]
        B --- E[ssh]
        E --> |File Transfer|B
        %% Note: Used 1 to place Disk higher in ordering
        A -- </br>-Original Job Ad</br>-Routed Job Ad --> 1[(Disk)]
    end
end
subgraph HM2[Remote Batch Sytem Host Machine]
    subgraph Remote Submit
        %%direction LR
        F[sshd] --> G[blahp]
        %% FTGahp capitalized to be legible
        H[sshd] --> I[FTGahp]
        I -- SSH Tunnel --> H
    end
end
%% -- External Nodes --
0>Job Ad]
%% -- External Nodes --
%% -- Subgraph Links --
D ===|Blahp:</br>-stdin</br>-stdout</br>-stderr| F
E ===|File:</br>-stdin</br>-stdout</br>-stderr| H
0 --> A
A == Ads ==> ZZ(((Central Collector)))
%% Stylize host machine boxes
style HM1 fill:#FFF,stroke:#000
style HM2 fill:#FFF,stroke:#000
%% -- Subgraph Links --
```
