# test_oskar_4.py
# study_update.py

import concurrent.futures
import json
import logging
import os
import sys
import setting_file

from astropy.io import fits
import matplotlib

matplotlib.use("Agg")
# pylint: disable=wrong-import-position
import matplotlib.pyplot as plt
import numpy
import oskar

from utils import get_start_time

axis_freq = [70.0,110.0]


LOG = logging.getLogger()

base_settings = setting_file.base_settings
fields = setting_file.fields
bright_sources = setting_file.bright_sources

def make_sky_model(sky0, settings, radius_deg, flux_min_outer_jy):
    """Filter sky model.

    Includes all sources within the given radius, and sources above the
    specified flux outside this radius.
    """
    # Get pointing centre.
    ra0_deg = float(settings["observation/phase_centre_ra_deg"])
    dec0_deg = float(settings["observation/phase_centre_dec_deg"])

    # Create "inner" and "outer" sky models.
    sky_inner = sky0.create_copy()
    sky_outer = sky0.create_copy()
    sky_inner.filter_by_radius(0.0, radius_deg, ra0_deg, dec0_deg)
    sky_outer.filter_by_radius(radius_deg, 180.0, ra0_deg, dec0_deg)
    sky_outer.filter_by_flux(flux_min_outer_jy, 1e9)
    LOG.info("Number of sources in sky0: %d", sky0.num_sources)
    LOG.info("Number of sources in inner sky model: %d", sky_inner.num_sources)
    LOG.info(
        "Number of sources in outer sky model above %.3f Jy: %d",
        flux_min_outer_jy,
        sky_outer.num_sources,
    )
    sky_outer.append(sky_inner)
    LOG.info(
        "Number of sources in output sky model: %d", sky_outer.num_sources
    )
    return sky_outer


def make_plot(prefix, field_name, metric_key, results, axis_freq):
    """Plot selected results."""
    # Get data.
    data = numpy.zeros_like(axis_freq)
    with numpy.nditer(
        [axis_freq, data], op_flags=[["readonly"], ["writeonly"]]
    ) as it:
        for freq, d in it:
            key = "%s_%s_%d_MHz_iono" % (prefix, field_name, freq)
            if key in results:
                d[...] = numpy.log10(results[key][metric_key])

    # Scatter plot.
    plt.scatter(axis_freq, data)

    # Title and axis labels.
    metric_name = "[ UNKNOWN ]"
    if metric_key == "image_centre_rms":
        metric_name = "Central RMS [Jy/beam]"
    elif metric_key == "image_medianabs":
        metric_name = "MEDIAN(ABS(image)) [Jy/beam]"
    sky_model = "GLEAM"
    if "A-team" in prefix:
        sky_model = sky_model + " + A-team"
    plt.title("%s for %s field (%s)" % (metric_name, field_name, sky_model))
    plt.xlabel("Frequency [MHz]")
    plt.ylabel("log10(%s)" % metric_name)
    plt.savefig("%s_%s_%s.png" % (prefix, field_name, metric_key))
    plt.close("all")

def make_vis_data(settings, sky):
    """Run simulation using supplied settings."""
    if os.path.exists(settings["interferometer/ms_filename"]):
        LOG.info("Skipping simulation, as output data already exist.")
        return
    LOG.info("Simulating %s", settings["interferometer/oskar_vis_filename"])
    # print(json.dumps(settings.to_dict(), indent=4))
    sim = oskar.Interferometer(settings=settings)
    sim.set_sky_model(sky)
    sim.run()

def make_diff_image_stats(
    filename1, filename2, use_w_projection, out_image_root=None
):
    """Make an image of the difference between two visibility data sets.

    This function assumes that the observation parameters for both data sets
    are identical. (It will fail horribly otherwise!)
    """
    # Set up an imager.
    (hdr1, handle1) = oskar.VisHeader.read(filename1)
    (hdr2, handle2) = oskar.VisHeader.read(filename2)
    frequency_hz = hdr1.freq_start_hz
    fov_ref_frequency_hz = 140e6
    fov_ref_deg = 5.0
    fov_deg = fov_ref_deg * (fov_ref_frequency_hz / frequency_hz)
    imager = oskar.Imager(precision="double")
    imager.set(
        fov_deg=fov_deg, image_size=8192, fft_on_gpu=True, grid_on_gpu=True
    )
    if out_image_root is not None:
        imager.output_root = out_image_root

    LOG.info("Imaging differences between '%s' and '%s'", filename1, filename2)
    block1 = oskar.VisBlock.create_from_header(hdr1)
    block2 = oskar.VisBlock.create_from_header(hdr2)
    if hdr1.num_blocks != hdr2.num_blocks:
        raise RuntimeError(
            "'%s' and '%s' have different dimensions!" % (filename1, filename2)
        )
    if use_w_projection:
        imager.set(algorithm="W-projection")
        imager.coords_only = True
        for i_block in range(hdr1.num_blocks):
            block1.read(hdr1, handle1, i_block)
            imager.update_from_block(hdr1, block1)
        imager.coords_only = False
        imager.check_init()
        LOG.info("Using %d W-planes", imager.num_w_planes)
    executor = concurrent.futures.ThreadPoolExecutor(2)
    for i_block in range(hdr1.num_blocks):
        tasks_read = []
        tasks_read.append(executor.submit(block1.read, hdr1, handle1, i_block))
        tasks_read.append(executor.submit(block2.read, hdr2, handle2, i_block))
        concurrent.futures.wait(tasks_read)
        block1.cross_correlations()[...] -= block2.cross_correlations()
        imager.update_from_block(hdr1, block1)
    del handle1, handle2, hdr1, hdr2, block1, block2

    # Finalise image and return it to Python.
    output = imager.finalise(return_images=1)
    image = output["images"][0]

    LOG.info("Generating image statistics")
    image_size = imager.image_size
    box_size = int(0.1 * image_size)
    centre = image[
        (image_size - box_size) // 2 : (image_size + box_size) // 2,
        (image_size - box_size) // 2 : (image_size + box_size) // 2,
    ]
    del imager
    return {
        "image_medianabs": numpy.median(numpy.abs(image)),
        "image_mean": numpy.mean(image),
        "image_std": numpy.std(image),
        "image_rms": numpy.sqrt(numpy.mean(image**2)),
        "image_centre_mean": numpy.mean(centre),
        "image_centre_std": numpy.std(centre),
        "image_centre_rms": numpy.sqrt(numpy.mean(centre**2)),
    }



def run_single(prefix_field, settings, sky, freq_MHz, out0_name, results):
    """Run a single simulation and generate image statistics for it."""
    out = "%s_%d_MHz_iono" % (prefix_field, freq_MHz)
    if out in results:
        LOG.info("Using cached results for '%s'", out)
        return
    settings["telescope/ionosphere_screen_type"] = "External"
    settings[
        "telescope/external_tec_screen/input_fits_file"
    ] = "../test_screen_60s.fits"
    settings["interferometer/oskar_vis_filename"] = out + ".vis"
    settings["interferometer/ms_filename"] = out + ".ms"
    make_vis_data(settings, sky)
    out_image_root = out
    use_w_projection = True
    if str(settings["interferometer/ignore_w_components"]).lower() == "true":
        use_w_projection = False
    results[out] = make_diff_image_stats(
        out0_name, out + ".vis", use_w_projection, out_image_root
    )

def run_set(prefix, base_settings, fields, axis_freq, plot_only):
    """Runs a set of simulations."""
    if not plot_only:
        # Load base sky model
        settings = oskar.SettingsTree("oskar_sim_interferometer")
        sky0 = oskar.Sky()

        # 研究fits结构
        if "GLEAM" in prefix:
            # Load GLEAM catalogue from FITS binary table.
            hdulist = fits.open("../GLEAM_EGC.fits")
            # pylint: disable=no-member
            cols = hdulist[1].data[0].array
            data = numpy.column_stack(
                (cols["RAJ2000"], cols["DEJ2000"], cols["peak_flux_wide"])
            )
            data = data[data[:, 2].argsort()[::-1]]
            print ("shape:{RA, DEC, peak_flux_wide}",data.shape)
            sky_gleam = oskar.Sky.from_array(data)
            sky0.append(sky_gleam) # 加入gleam数据
        if "A-team" in prefix:
            sky_bright = oskar.Sky.from_array(bright_sources())
            sky0.append(sky_bright) # 加入背景亮度

    # Iterate over fields.
    for field_name, field in fields.items():
        # Load result set, if it exists.
        prefix_field = prefix + "_" + field_name
        print (prefix_field) # 看一下
        
        results = {}
        json_file = prefix_field + "_results.json"
        if os.path.exists(json_file):
            with open(json_file, "r") as input_file:
                results = json.load(input_file) # 暂时不知道用处
        # Iterate over frequencies.
        if not plot_only:
            for freq_MHz in axis_freq:
                # Update settings for field.
                settings_dict = base_settings.copy()
                settings_dict.update(field)
                settings.from_dict(settings_dict)
                ra_deg = float(settings["observation/phase_centre_ra_deg"])
                length_sec = float(settings["observation/length"])
                settings["observation/start_frequency_hz"] = freq_MHz * 1e6
                settings["observation/start_time_utc"] = get_start_time(
                    ra_deg, length_sec
                )

                # Create the sky model.
                sky = make_sky_model(sky0, settings, 20.0, 10.0)
                settings["interferometer/ignore_w_components"] = "true"
                if "A-team" in prefix:
                    settings["interferometer/ignore_w_components"] = "false"

                # Simulate the 'perfect' case.
                out0 = "%s_%d_MHz_no_errors" % (prefix_field, freq_MHz)
                settings["telescope/ionosphere_screen_type"] = "None"
                settings["telescope/external_tec_screen/input_fits_file"] = ""
                settings["interferometer/oskar_vis_filename"] = out0 + ".vis"
                settings["interferometer/ms_filename"] = out0 + ".ms"
                # print (settings.to_dict())
                # make_vis_data(settings, sky)

                # Simulate the error case.
                run_single(
                    prefix_field,
                    settings,
                    sky,
                    freq_MHz,
                    out0 + ".vis",
                    results,
                )

        # # Generate plot for the field.
        # make_plot(prefix, field_name, "image_centre_rms", results, axis_freq)
        # make_plot(prefix, field_name, "image_medianabs", results, axis_freq)

        # # Save result set.
        # with open(json_file, "w") as output_file:
        #     json.dump(results, output_file, indent=4)

plot_only = False
run_set("GLEAM_A-team", base_settings, fields, axis_freq, plot_only)
