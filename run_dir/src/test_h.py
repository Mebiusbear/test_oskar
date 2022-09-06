
freqs = [1,2,3]
a = dict()
# template_params = {
#     "image/fov_deg": 5.5,
#     "image/size": 8192,
#     "image/algorithm": "W-projection",
#     "image/fft/use_gpu": True,
#     "image/fft/grid_on_gpu": True,
#     "image/input_vis_data": "./GLEAM_A-team_EoR0_%d_MHz_no_errors.ms"%freq,
#     "image/root_path": "../fits_data/%d_MHz_iono"%freq
# }
for freq in freqs:
    a.update({"%d_MHz"%freq : 
        {
            "image/fov_deg": 5.5,
            "image/size": 8192,
            "image/algorithm": "W-projection",
            "image/fft/use_gpu": True,
            "image/fft/grid_on_gpu": True,
            "image/input_vis_data": "./GLEAM_A-team_EoR0_%d_MHz_no_errors.ms"%freq,
            "image/root_path": "../fits_data/%d_MHz_iono"%freq
        }
    })
print (a)
