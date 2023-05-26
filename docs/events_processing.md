# Events processing

General processing strategy for events information is to:
- make use of both channel based events information and external file based information
- compare + verify + reformat into a single `CSV` file
- select relevant events and save as `FIF` data

> **_NOTE:_**
> `blue`: MNE python data
> `green`: `CSV`, `TSV` or other data format
> `red`: process
> `violet`: dataset specific reformatted `CSV` file

```mermaid
graph TD
    %% Processes
    classDef process fill: #b21, stroke-width: 5px, stroke: #777
    
    %% Data
    classDef mne_data fill: #05c, stroke-width: 5px, stroke: #777
    classDef specific_data fill: #55c, stroke-width: 5px, stroke: #777
    classDef optional_data fill: #260, stroke-width: 5px, stroke: #777, stroke-dasharray: 5 5

    %% Initial tidying, sanity check
    mne_events("MNE events"):::mne_data --> compare_events(["compare/reformat events"]):::process;
    external_files("External files (CSV, TSV etc.)"):::optional_data -.-> compare_events;
    compare_events --> formatted("Formatted events (CSV)"):::specific_data;
    
    %% Selection of relevant events
    formatted --> select(["select.py"]):::process;
    select --> selected(["selected events (FIF)"]):::mne_data;
```