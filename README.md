# how to use oskar in singularity

## part 1

```python
# setting_file.py
base_settings = {
    "simulator": {
        "double_precision": True,
        "use_gpus": True,
        "cuda_device_ids":"1,2,3", # "0"
        "max_sources_per_chunk": 16384,
        "keep_log_file":True,
        "write_status_to_log_file":True,
    },
    "observation": {
        "frequency_inc_hz": 100e3,
        "length": 14400.0,
        "num_time_steps": 240,
    },
    "telescope": {
        "input_directory": "../telescope_data/SKA1-LOW_SKO-0000422_Rev3_38m_SKALA4_spot_frequencies.tm",
        "pol_mode": "Full",
    },
    "interferometer": {
        "channel_bandwidth_hz": 100e3,
        "time_average_sec": 1.0,
        "max_time_samples_per_block": 4,
    },
}
```

## part 2
```
singularity shell --nv -H $PWD oskar_python3_cuda114_newest.sif
cd run_dir

rm -r *fits *vis *ms *log && python3 src/main.py

main.py ionosphere line-183
```

## part 3
```python
# app_imager.py
freqs = [50,70]
# ---------------------------------------------
mkdir fits_data
python3 app_imager.py

```

## part 4

```
cd arch_data/arch....
python ../../run_dir/src/app_plot.py
```
