# app_plot.py

from re import I
import matplotlib.pyplot as plt
import numpy as np
import os
import astropy.io.fits as fits
import argparse


fits_list = ["50_MHz_no_errors_I.fits","50_MHz_iono_I.fits"]
# fits_list = ["70_MHz_no_errors_I.fits","70_MHz_iono_I.fits"]
# fits_list = ["110_MHz_no_errors_I.fits","110_MHz_iono_I.fits"]
# fits_list = ["230_MHz_no_errors_I.fits","230_MHz_iono_I.fits"]

fits_dir = "./"
fits_list = os.listdir(fits_dir)

freq_list = ["50","70","110"]

im_list = np.zeros((len(freq_list),2,8192,8192))

for i,freq in enumerate(freq_list):
    for fits_name in fits_list:
        if freq in fits_name and "fits" in fits_name:
            if "errors" in fits_name:
                im_list[i][0] = fits.open(fits_name)[0].data[0]
            else:
                im_list[i][1] = fits.open(fits_name)[0].data[0]


    
def fits_duibi(im_list):
    for i,im_pair in enumerate(im_list):
        residual = im_pair[0] - im_pair[1]
        RMS = np.sum(np.power(residual,2)) / np.power(residual.shape[0],2)
        print ("{:.3e}".format(RMS))

        plt.figure(figsize=(16,7))

        plt.subplot(131)
        plt.imshow(im_pair[0],cmap="gray")
        plt.title("no_error")
        plt.axis("off")
        plt.colorbar(orientation='horizontal')

        plt.subplot(132)
        plt.imshow(im_pair[1],cmap="gray")
        plt.title("iono")
        plt.axis("off")
        plt.colorbar(orientation='horizontal')

        plt.subplot(133)
        plt.imshow(residual,cmap="gray")
        plt.title("residual")
        plt.text(x=0,y=0,s="RMS:{:.3e}".format(RMS))
        plt.axis("off")
        plt.colorbar(orientation='horizontal')

        plt.savefig("%s_Hz.png"%freq_list[i])


fits_duibi(im_list)


# def fits_duibi(name,fits_list):
#     im_list = list()
#     for i in fits_list:
#         fits_path = os.path.join("./",i)
#         im_list.append(fits.open(fits_path)[0].data[0])

#     residual = im_list[0] - im_list[1]
#     RMS = np.sum(np.power(residual,2)) / np.power(residual.shape[0],2)

#     print ("{:.3e}".format(RMS))

#     im_list.append(residual)

#     plt.figure(figsize=(16,9))

#     plt.subplot(131)
#     plt.imshow(im_list[0],cmap="gray")
#     plt.title("no_error")
#     plt.axis("off")
#     plt.colorbar(orientation='horizontal')

#     plt.subplot(132)
#     plt.imshow(im_list[1],cmap="gray")
#     plt.title("iono")
#     plt.axis("off")
#     plt.colorbar(orientation='horizontal')

#     plt.subplot(133)
#     plt.imshow(im_list[2],cmap="gray")
#     plt.title("residual")
#     plt.text(x=0,y=0,s="{:.3e}".format(RMS))
#     plt.axis("off")
#     plt.colorbar(orientation='horizontal')

#     plt.savefig(name)


# fits_duibi(fits_list[1][:-12]+".png",fits_list)