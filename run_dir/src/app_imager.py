
import oskar



# for freq in freqs:
# params_img = {
#     "image/fov_deg": 5.5,
#     "image/size": 8192,
#     "image/algorithm": "W-projection",
#     "image/fft/use_gpu": True,
#     "image/fft/grid_on_gpu": True,
#     "image/input_vis_data": "./GLEAM_A-team_EoR0_%d_MHz_no_errors.ms"%freq,
#     "image/root_path": "../fits_data/%d_MHz_iono"%freq
# }
freqs = [70,110]
params_dict = dict()
for freq in freqs:
    params_img = {
            "image/fov_deg": 5.5,
            "image/size": 8192,
            "image/algorithm": "W-projection",
            "image/fft/use_gpu": True,
            "image/fft/grid_on_gpu": True,
            "image/input_vis_data": "./GLEAM_A-team_EoR0_%d_MHz_no_errors.ms"%freq,
            "image/root_path": "../fits_data/%d_MHz_iono"%freq
        }

    # Make image.
    settings_img = oskar.SettingsTree("oskar_imager")
    settings_img.from_dict(params_img)
    imager = oskar.Imager(settings=settings_img)
    imager.run()