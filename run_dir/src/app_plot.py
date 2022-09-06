# app_plot.py

import matplotlib.pyplot as plt
import numpy as np

import argparse


# def main():
#     parser = argparse.ArgumentParser(description="Demo of argparse")

#     parser.add_argument('-n','--image_name', default='Hello.png')
#     parser.add_argument('-m','--multi_p', default='False')
#     parser.add_argument('-s','--single_p', default='False')

#     args = parser.parse_args()
#     # image_name = args.image_name
#     # multi_plot = args.multi_plot
#     # single_plot = args.single_plot

#     if args.single_p:
#         pass

#     if args.multi_p:
#         multi_plot(args.image_name,image_list)
        
#     im = np.load("imager_test.npy")




# def multi_plot(image_name,image_list):
#     plt.subplot(131)
#     plt.subplot(132)
#     plt.subplot(133)

#     # plt.colorbar()

#     plt.savefig(image_name)




import astropy.io.fits as fits

fits_list = ["50_MHz_noerror_I.fits","50_MHz_iono_I.fits"]
fits_list = ["70_MHz_noerror_I.fits","70_MHz_iono_I.fits"]
fits_list = ["110_MHz_noerror_I.fits","110_MHz_iono_I.fits"]
fits_list = ["230_MHz_noerror_I.fits","230_MHz_iono_I.fits"]

def fits_duibi(name,fits_list):
    im_list = list()
    for i in fits_list:
        fits_path = "/".join(["fits_data",i])
        im_list.append(fits.open(fits_path)[0].data[0])

    residual = im_list[0] - im_list[1]
    RMS = np.sum(np.power(residual,2)) / np.power(residual.shape[0],2)

    print ("{:.3e}".format(RMS))

    im_list.append(residual)

    plt.figure(figsize=(16,9))

    plt.subplot(131)
    plt.imshow(im_list[0],cmap="gray")
    plt.title("no_error")
    plt.axis("off")
    plt.colorbar(orientation='horizontal')

    plt.subplot(132)
    plt.imshow(im_list[1],cmap="gray")
    plt.title("iono")
    plt.axis("off")
    plt.colorbar(orientation='horizontal')

    plt.subplot(133)
    plt.imshow(im_list[2],cmap="gray")
    plt.title("residual")
    plt.text(x=0,y=0,s="{:.3e}".format(RMS))
    plt.axis("off")
    plt.colorbar(orientation='horizontal')

    plt.savefig(name)

fits_duibi("50_MHz.png",fits_list)