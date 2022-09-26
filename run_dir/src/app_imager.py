
import oskar
import setting_file

freqs = [50,70,110]
for freq in freqs:
    params_img = setting_file.params_img(freq,output_dir="origin_fits_data",error=False) # noerror : Flase
    # Make image.
    settings_img = oskar.SettingsTree("oskar_imager")
    settings_img.from_dict(params_img)
    imager = oskar.Imager(settings=settings_img)
    imager.run()
    params_img = setting_file.params_img(freq,output_dir="origin_fits_data",error=True) # noerror : Flase
    # Make image.
    settings_img = oskar.SettingsTree("oskar_imager")
    settings_img.from_dict(params_img)
    imager = oskar.Imager(settings=settings_img)
    imager.run()