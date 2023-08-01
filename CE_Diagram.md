CE Overview
===
``` mermaid
flowchart LR %% Specify diagram type and direction

%% ID FORMAT:
%% - External nodes are numbered (0 - 100)
%% - Internal nodes are alphabetic (A - Z)
%% - Nodes within nested subgraphs are
%%   are labelled by double letters (AA - ZZ)
%% - All subgraph names are capitalized (Blahp)
%%   while nodes with the same name are lowercase (blahp)

subgraph HTCondor-CE
	direction LR
	A(Job Router) --> B[[CE schedd]]
	B --> C{Grid Mgr.}
	D[(Log)] --> C
end

subgraph Blahp
	direction LR
	subgraph lsf_*.sh %% Configure nested subgraphs above internal nodes
		direction LR %% Set direction of isolated subgraphs
		AA[submit] ---|OR| BB[cancel]
		BB ---|OR| CC[status]
	end
	E[[blahp]] --> lsf_*.sh
	F[common_sub</br>_attr.sh] --> lsf_*.sh
	lsf_*.sh --> F
end

subgraph Batch Sys
	direction LR
	G((qsub))
end

%% -- External Nodes --
0>Job Ad]
%% -- External Nodes --
```
