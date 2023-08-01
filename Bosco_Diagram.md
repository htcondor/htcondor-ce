Bosco Overview
===
```mermaid
flowchart LR %% Specify diagram type and direction

%% ID FORMAT:
%% - External nodes are numbered (0 - 100)
%% - Internal nodes are alphabetic (A - Z)
%% - Nodes within nested subgraphs are
%%   are labelled by double letters (AA - ZZ)
%% - All subgraph names are capitalized (Blahp)
%%   while nodes with the same name are lowercase (blahp)

subgraph Bosco Cluster
  direction LR
  A[schedd] --> B[Grid</br>Manager]
  C[SP] --> B
  B --- D[ssh]
  B --- E[ssh]
  E --> |FT|B
  C -. Data Channel .- E
end

subgraph Remote Submit
  direction LR
  F[sshd] --> G[blahp]
  H[sshd] --> I[FTGahp] %% FTGahp capitalized to be legible
end

%% -- External Nodes --
0>Job Ad]
%% -- External Nodes --
```
