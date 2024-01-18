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
### HTCondor-CE workflow
``` mermaid
flowchart LR

%% ID FORMAT:
%% - External nodes are numbered (0 - 100)
%% - Internal nodes are alphabetic (A - Z)
%% - Nodes within nested subgraphs are
%%   are labelled by double letters (AA - ZZ)
%% - All subgraph names are capitalized (Blahp)
%%   while nodes with the same name are lowercase (blahp)

subgraph HTCondor-CE
	%%direction LR %% Flowchart direction statement overrides statements in connected subgraphs; comment these out.
	A[[SchedD]] --> B(Job Router)
	B -. Routed Job .-> A
	A -.-> C{Grid Manager}
	D[(Log)] --- C
end

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

subgraph Batch System
	%%direction LR
	G((qsub))
end

%% -- External Nodes --
0>Job Ad]
%% -- External Nodes --

%% -- Subgraph Links --
C <--> E
lsf_*.sh ---> G
0 --> A
%% -- Subgraph Links --
```

### Bosco Cluster workflow
```mermaid
flowchart LR

%% ID FORMAT:
%% - External nodes are numbered (0 - 100)
%% - Internal nodes are alphabetic (A - Z)
%% - Nodes within nested subgraphs are
%%   are labelled by double letters (AA - ZZ)
%% - All subgraph names are capitalized (Blahp)
%%   while nodes with the same name are lowercase (blahp)

subgraph Bosco Cluster
  %%direction LR %% Flowchart direciton statement overrides statements in connected subgraphs; comment these out
  A[[SchedD]] --> B{Grid</br>Manager}
  C[SP] --> B
  B --- D[ssh]
  B --- E[ssh]
  E --> |FT|B
  C -. Data Channel .- E
end

subgraph Remote Submit
  %%direction LR
  F[sshd] --> G[blahp]
  %% FTGahp capitalized to be legible
  H[sshd] --> I[FTGahp]
end

%% -- External Nodes --
0>Job Ad]
%% -- External Nodes --

%% -- Subgraph Links --
D ===|Blahp:</br>-stdin</br>-stdout</br>-stderr| F
E ===|File:</br>-stdin</br>-stdout</br>-stderr| H
0 --> A
%% -- Subgraph Links --
```
