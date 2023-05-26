# Parameter JSON file description

`name`: give a name to current run of the pipeline

`dst_root`: directory in which all results are stored. Each run will be stored inside
a directory `dst_root/name`

`dataset`: name of the dataset, must be supported

`target`: name of the target file type
* `filtered_raw`: filtered raw object
* `ica_raw`: ICA reconstructed raw
* `epochs`: epochs
* `noise_cov`: noise covariance
* `inv`: inverse operator
* `stc`: source estimates
* `fs_recon`: FreeSurfer reconstruction
* `source_space`: source space
* `bem`: BEM model
* `trans`: Head-MRI trans
* `fwd`: forward solution

`filter`: filter parameters
* `l_freq`: high-pass frequency
* `h_freq`: low-pass frequency


```json
{
  "name": "test",
  "dst_root": "",
  "dataset": "sample",
  "target": "target-file",
  "filter":
  {
    "l_freq": 0.1,
    "h_freq": 20
  }
}
```