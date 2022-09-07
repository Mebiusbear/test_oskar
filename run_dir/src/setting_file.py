import numpy
import os

base_settings = {
    "simulator": {
        "double_precision": True,
        "use_gpus": True,
        "cuda_device_ids":"0,1,2,3",
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

def params_img(freq,output_dir,error=False):
    if not os.path.exists("../%s"%output_dir):
        os.mkdir("../%s"%output_dir)
    if not error:
        noerror = "_no_errors"
    else:
        noerror = "_iono"
    return {
            "image/fov_deg": 5.5,
            "image/size": 8192,
            "image/algorithm": "W-projection",
            "image/fft/use_gpu": True,
            "image/fft/grid_on_gpu": True,
            "image/input_vis_data": "./GLEAM_A-team_EoR0_%d_MHz%s.ms"%(freq,noerror),
            "image/root_path": "../%s/%d_MHz%s"%(output_dir,freq,noerror)
        }


# Define axes of parameter space.
fields = {
    "EoR0": {
        "observation/phase_centre_ra_deg": 0.0,
        "observation/phase_centre_dec_deg": -27.0,
    },
    "EoR1": {
        "observation/phase_centre_ra_deg": 60.0,
        "observation/phase_centre_dec_deg": -30.0,
    },
    "EoR2": {
        "observation/phase_centre_ra_deg": 170.0,
        "observation/phase_centre_dec_deg": -10.0,
    },
}

def bright_sources():
    """Returns a list of bright A-team sources."""
    # Sgr A: guesstimates only!
    # For A: data from the Molonglo Southern 4 Jy sample (VizieR).
    # Others from GLEAM reference paper, Hurley-Walker et al. (2017), Table 2.
    return numpy.array((
        [266.41683, -29.00781,  2000,0,0,0, 0,  0, 0,  3600, 3600, 0],
        [ 50.67375, -37.20833,   528,0,0,0, 178e6, -0.51, 0, 0, 0, 0],  # For
        [201.36667, -43.01917,  1370,0,0,0, 200e6, -0.50, 0, 0, 0, 0],  # Cen
        [139.52500, -12.09556,   280,0,0,0, 200e6, -0.96, 0, 0, 0, 0],  # Hyd
        [ 79.95833, -45.77889,   390,0,0,0, 200e6, -0.99, 0, 0, 0, 0],  # Pic
        [252.78333,   4.99250,   377,0,0,0, 200e6, -1.07, 0, 0, 0, 0],  # Her
        [187.70417,  12.39111,   861,0,0,0, 200e6, -0.86, 0, 0, 0, 0],  # Vir
        [ 83.63333,  22.01444,  1340,0,0,0, 200e6, -0.22, 0, 0, 0, 0],  # Tau
        [299.86667,  40.73389,  7920,0,0,0, 200e6, -0.78, 0, 0, 0, 0],  # Cyg
        [350.86667,  58.81167, 11900,0,0,0, 200e6, -0.41, 0, 0, 0, 0]   # Cas
        ))

