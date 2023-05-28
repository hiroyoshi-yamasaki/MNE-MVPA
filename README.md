# MNE-MVPA
An extension of MNE-python to perform Multi-Variate Pattern Analysis.

```mermaid
graph TD
    %% Processes
    classDef automatic_process fill: #b21, stroke-width: 5px, stroke: #777
    classDef manual_process fill: #c71, stroke-width: 5px, stroke: #777, stroke-dasharray: 5, 5;
    
    %% Data
    classDef mne_data fill: #05c, stroke-width: 5px, stroke: #777
    classDef event_data fill: #260, stroke-width: 5px, stroke: #777
    classDef other_data fill: #55c, stroke-width: 5px, stroke: #777

    %% Preprocessing MEG data
    subgraph "Preprocessing"
    
        %% Manual check for bad channels, artefacts etc.
        raw_data("Raw"):::mne_data -.-> check_raw(["Check for bad data"]):::manual_process;
        check_raw -.-> checked_raw("Checked raw"):::mne_data;
        
        %% Filter the raw files
        checked_raw --> filter_raw(["filter.py"]):::automatic_process;
        filter_raw --> filtered_raw("Filtered raw"):::mne_data;
        
        %% Artefact removal with ICA
        filtered_raw --> ica(["ica.py"]):::automatic_process;
        ica --> recon_raw("Reconstructed raw"):::mne_data;
        filtered_raw -.-> man_ica(["manual ICA"]):::manual_process;
        man_ica -.-> recon_raw;
    end
    
    %% Processes specific to datasets (event processing)
    subgraph "Dataset specific event processes"
        selected_events("selected_events"):::event_data;
    end
    
    %% Epoching
    recon_raw --> epoch(["epoch.py"]):::automatic_process;
    selected_events --> epoch;
    epoch --> epochs("Epoched data"):::mne_data;
    
    subgraph "Forward Solution"
        
        %% Make a FreeSurfer surface reconstruction
        T1("T1"):::other_data --> recon(["reconstruct.sh"]):::automatic_process;
        recon --> fs_surface("FreeSurfer surface"):::other_data;
        
        %% Create BEM
        fs_surface --> make_bem(["make-bem.sh"]):::automatic_process;
        make_bem --> bem("BEM"):::other_data;
        
        %% Source space
        fs_surface --> make_src(["setup_source_space"]):::automatic_process;
        make_src --> src("Source space"):::mne_data;
        
        %% Coregistration
        info("Info"):::mne_data --> coreg(["coregistration.py"]):::automatic_process;
        info -.-> man_coreg(["Manual coregistration"]):::manual_process;
        
        coreg --> trans("Head-MRI trans"):::mne_data;
        man_coreg -.-> trans;
        
        %% Make forward solution
        trans --> make_fwd(["forward_solution.py"]):::automatic_process;
        src --> make_fwd;
        bem --> make_fwd;
        make_fwd --> fwd("Forward solution"):::mne_data;
    end
    
    subgraph "Source Estimation"
        
        %% Calculate noise covariance matrix
        epochs --> noise_cov(["compute_covariance"]):::automatic_process;
        noise_cov --> cov("Noise covariance"):::mne_data;
        
        %% Make an inverse operator
        fwd --> make_inv(["make_inv.py"]):::automatic_process;
        cov --> make_inv;
        make_inv --> inv("Inverse operator"):::mne_data;
        
        %% Estimate source
        epochs --> estimate(["Source estimation"]):::automatic_process;
        inv --> estimate;
        estimate --> stc("Source estimate"):::mne_data;
    end
```