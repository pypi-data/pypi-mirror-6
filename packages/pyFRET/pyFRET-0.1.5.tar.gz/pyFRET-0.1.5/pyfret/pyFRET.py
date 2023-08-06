"""
Copyright (c) 2014 Rebecca R. Murphy
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

import array
import os
import sys
import struct
import math as ma
import csv

try:
    from scipy.optimize import curve_fit
    import matplotlib
    import numpy as np
    from matplotlib import pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib import cm


    # matplotlib customizations
    matplotlib.rc('xtick', labelsize=18) 
    matplotlib.rc('ytick', labelsize=18) 
    font = {'family' : 'sans',
            'weight' : 'normal',
            'size'   : 18}

    matplotlib.rc('font', **font)
except:
    print "Numerical libraries not present in your systems"
    pass


class FRET_data:

    """
    This class holds single molecule data.

    It has two attributes, donor and acceptor to hold photon counts from the donor and acceptor channels respectively.
    These are numpy arrays.

    It can be initialized from two lists or two arrays of photon counts: data = FRET_data(donor_events_list, acceptor_events_list)

    """

    def __init__(self, donor, acceptor):
        """
        Initialize the FRET data object.

        Arguments:

        * donor: list or array of donor time-bins
        * acceptor: list or array of acceptor time-bins.

        """
        self.donor = np.array(donor).astype(float)
        self.acceptor = np.array(acceptor).astype(float)

    def subtract_bckd(self, bckd_d, bckd_a):
        """
        Subtract background noise from donor and acceptor channel data.

        Arguments:

        * bckd_d: average noise per time-bin in the donor channel
        * bckd_a: average noise per time-bin in the acceptor channel
        """
        self.donor = self.donor - bckd_d
        self.acceptor = self.acceptor - bckd_a 
        return self


    def subtract_crosstalk(self, ct_d, ct_a):
        """
        Subtract crosstalk from donor and acceptor channels.

        Arguments:

        * ct_d: fractional cross-talk from donor to acceptor (float between 0 and 1)
        * ct_a: fractional cross-talk from acceptor to donor (float between 0 and 1)
        """
        donor_cross_talk = self.donor * ct_d
        acceptor_cross_talk = self.acceptor * ct_a
        self.donor = self.donor - acceptor_cross_talk
        self.acceptor = self.acceptor - donor_cross_talk
        return self
        

    def threshold_AND(self, D_T, A_T):
        """
        Select data based on the AND thresholding criterion.

        Arguments:

        * D_T: threshold for the donor channel
        * A_T: threshold for the acceptor channel

        An event is above threshold if nD > donor_threshold AND nA > acceptor_threshold
        for nD and nA photons in the donor and acceptor channels respectively
        """
        select = (self.donor > D_T) & (self.acceptor > A_T)
        self.donor = self.donor[select]
        self.acceptor = self.acceptor[select]
        return self
        
    def threshold_OR(self, D_T, A_T):
        """
        Select data based on the OR thresholding criterion.

        Arguments:

        * D_T: threshold for the donor channel
        * A_T: threshold for the acceptor channel

        An event is above threshold in nD > donor_threshold OR nA > acceptor_threshold
        for nD and nA photons in the donor and acceptor channels respectively
        """
        select = (self.donor > D_T) | (self.acceptor > A_T)
        self.donor = self.donor[select]
        self.acceptor = self.acceptor[select]
        return self

    def threshold_SUM(self, T):
        """
        Select data based on the SUM thresholding criterion.

        Arguments:
        T: threshold above which a time-bin is accepted as a fluorescent burst

        An event is above threshold in nD  + nA > threshold
        for nD and nA photons in the donor and acceptor channels respectively
        """
        select = (self.donor + self.acceptor > T)
        self.donor = self.donor[select]
        self.acceptor = self.acceptor[select]
        return self

    def proximity_ratio(self, gamma=1.0):
        """
        Calculate the proximity ratio (E) and return an array of values.

        Arguments:
        None    

        Keyword arguments:

        * gamma (default value 1.0): the instrumental gamma-factor

        Calculation: 

        E = nA / (nA + gamma*nD) for nA and nD photons in the acceptor and donor channels respectively
        """
        E = self.acceptor / (self.acceptor + (gamma * self.donor))
        return E

    def make_3d_plot(self, filepath, imgname, imgtype="pdf", labels = ["Donor", "Acceptor", "Frequency"]):
        """
        Make a 3D histogram of donor and acceptor photon counts.

        Arguments:

        * filepath: path to folder where data will be saved
        * filename: name of image file to save plot

        Keyword arguments:

        * filetype: image type (as string). Default "pdf". Accepted values: jpg, tiff, rgba, png, ps, svg, eps, pdf
        * labels: axes labels, list of strings ["Xtitle", "Ytitle", "Ztitle"]. Default ["Donor", "Acceptor", "Frequency"]
        """

        fullname = ".".join([imgname, imgtype])
        max_val = max(max(self.donor), max(self.acceptor))
        big_matrix = np.zeros((ma.ceil(max_val)+1, ma.ceil(max_val)+1))
        for (i, j) in zip(self.donor, self.acceptor):
            big_matrix[i][j] += 1

        fig = plt.figure()
        ax = fig.gca(projection="3d")
        ax.locator_params(nbins=4)
        X = np.arange(0, max_val+1, 1)
        Y = np.arange(0, max_val+1, 1)
        X, Y = np.meshgrid(X, Y)
        surf = ax.plot_surface(X, Y, big_matrix, rstride=1, cstride=1, cmap=cm.coolwarm,
                linewidth=0, antialiased=False)
        #fig.colorbar(surf, shrink=0.5, aspect=5)
        ax.set_xlabel("\n%s" %labels[0])
        ax.set_ylabel("\n%s" %labels[1])
        ax.set_zlabel("\n%s" %labels[2])
        figname = os.path.join(filepath, fullname)
        plt.savefig(figname)
        plt.close()
        return self

    def make_hex_plot(self, filepath, imgname, imgtype="pdf", labels = ["Donor", "Acceptor"], xmax = None, ymax = None, binning=None):
        """
        Make a 2D representation of donor and acceptor photon count frequencies.

        Based on the matplotlib.pyplot construction "hexbin": http://matplotlib.org/api/pyplot_api.html

        Arguments:

        * filepath: path to folder where data will be saved
        * imgname: name of image file to save plot

        Keyword arguments:

        * imgtype: image type (as string). Default "pdf". Accepted values: jpg, tiff, rgba, png, ps, svg, eps, pdf
        * labels: axes labels, list of strings ["Xtitle", "Ytitle"]. Default ["Donor", "Acceptor"]
        * xmax: maximum x-axis value. Default None (maximum will be the brightest donor event)
        * ymax: maximum x-axis value. Default None (maximum will be the brightest acceptor event)
        * binning: type of binning to use for plot. Default: None (bin colour corresponds to frequency). 
            Accepted vals: "log" (bin colour corresponds to frequency), integer (specifies number of bins), sequence (specifies bin lower bounds)
        """

        fullname = ".".join([imgname, imgtype])
        plt.hexbin(self.donor, self.acceptor, bins=binning)
        plt.colorbar()
        plt.xlabel("\n%s" %labels[0])
        plt.ylabel("\n%s" %labels[1])
        figname = os.path.join(filepath, fullname)
        if (xmax != None) & (ymax != None):
            plt.xlim(0, xmax)
            plt.ylim(0, ymax)
        plt.savefig(figname)
        plt.close()
        return self

    def build_histogram(self, filepath, csvname, gamma=1.0, bin_min=0.0, bin_max=1.0, bin_width=0.02, image = False, imgname = None, imgtype=None, gauss = True, gaussname = None):
        """
        Build a proximity ratio histogram and save the frequencies and bin centres as a csv file. 
        Optionally plot and save a graph and perform a simple gaussian fit.

        Arguments:

        * E: array of FRET efficiecies
        * filepath: path to folder where the histogram will be saved (as a string)
        * csvname: the name of the file in which the histogram will be saved (as a string)

        Keyword arguments:

        * gamma: Instrumental gamma factor. (float, default value 1.0)
        * bin_min: the minimum value for a histogram bin (default 0.0)
        * bin_max: the maximum value for a histogram bin (default 1.0)
        * bin_width: the width of one bin (default 0.02)
        * image: Boolean. True plots a graph of the histogram and saves it (default False)
        * imgname: the name of the file in which the histogram graph will be saved (as a string)
        * imgtype: filetype of histogram image. Accepted values: jpg, tiff, rgba, png, ps, svg, eps, pdf
        * gauss: Boolean. True will fit the histogram with a single gaussian distribution (default False)
        * gaussname: the name of the file in which the parameters of the Gaussian fit will be saved
        """

        E = self.proximity_ratio(gamma)

        csv_title = ".".join([csvname, "csv"])
        csv_full = os.path.join(filepath, csv_title)
        with open(csv_full, "w") as csv_file:
            bins = np.arange(bin_min, bin_max, bin_width)
            freq, binss, _ = plt.hist(E, bins, facecolor = "grey")
            bin_centres = []
            for i in range(len(binss)-1):
                bin_centres.append((binss[i+1] + binss[i])/2)
            for bc, fr in zip(bin_centres, freq):
                csv_file.write("%s, %s \n" %(bc, fr))
        if image == True:
            img_name = ".".join([imgname, imgtype])
            img_path = os.path.join(filepath, img_name)
            plt.xlabel("FRET Efficiency")
            plt.ylabel("Number of Events")
            plt.savefig(img_path)
            plt.cla()
        if gauss == True and gaussname != None:
            coeff, var_matrix, hist_fit = _fit_gauss(bin_centres, freq, p0=[1.0, 0.0, 1.0])
            bins = np.arange(0, 1, 0.02)
            plt.hist(E, bins, label='Test data', facecolor = "grey")
            plt.plot(bin_centres, hist_fit, label='Fitted data')
            plt.xlabel("FRET Efficiency")
            plt.ylabel("Number of Events")
            gauss_title = ".".join([gaussname, imgtype])
            gauss_title = os.path.join(filepath, gauss_title)
            plt.savefig(gauss_title)

            csv_title = ".".join([gaussname, "csv"])
            csv_full = os.path.join(filepath, csv_title)
            csv_file = open(csv_full, "w")
            
            csv_file.write("Coefficients\n")
            coeffs = ", ".join(map(str, coeff))
            csv_file.write("%s" %coeffs)

            csv_file.write("\n\nVariance Matrix\n")
            for lin in var_matrix:
                for v in lin:
                    csv_file.write("%s," %v)
                csv_file.write("\n")
            
            csv_file.write("\nGauss Frequencies\n")
            #fr = ", ".join(map(str, hist_fit))
            for bc, fr in zip(bin_centres, hist_fit):
                csv_file.write("%s, %s\n" %(bc, fr))


            #csv_file.write(var_matrix)
            #csv_file.write(hist_fit)
            csv_file.close()            
        plt.close()
        return self


def parse_csv(filepath, filelist, delimiter=","):
    """
    Read data from a list of csv and return a FRET_data object.

    Arguments:

    * filepath: the path to the folder containing the files
    * filelist: list of files to be analysed

    Keyword arguments:

    * delimiter (default ","): the delimiter between values in a row of the csv file.

    This function assumes that each row of your file has the format:
    "donor_item,acceptor_item" 

    If your data does not have this format (for example if you have separate files for donor and acceptor data), this function will not work well for you.
    """
    donor_data = []
    acceptor_data = []
    for fp in filelist:
        current_file = os.path.join(filepath, fp)
        with open(current_file) as csv_file:
            current_data = csv.reader(csv_file, delimiter=',')
            for row in current_data:
                donor_data.append(float(row[0]))
                acceptor_data.append(float(row[1]))
    FRET_data_obj = FRET_data(donor_data, acceptor_data)
    return FRET_data_obj

def parse_bin(filepath, filelist, bits=8):
    """
    Read data from a list of binary files and return a FRET_data object.

    Arguments:

    * filepath: the path to the folder containing the files
    * filelist: list of files to be analysed

    Keyword arguments:

    * bits (default value 8): the number of bits used to store a donor-acceptor pair of time-bins

    **Note: This file structure is probably specific to the Klenerman group's .dat files.**
        **Please don't use it unless you know you have the same filetype!** 
    """
    byte_order = sys.byteorder
    try:
        if byte_order == "little":
            edn = '>ii'
        elif byte_order == "big":
            edn = '<ii'
    except ValueError:
        print "Unknown byte order"
        raise
    donor_data = []
    acceptor_data = []
    for fp in filelist:
        current_file = os.path.join(filepath, fp)
        counter = 0
        data = []
        with open(current_file, "rb") as f:
            x = f.read(bits)
            while x:
                data.append(struct.unpack(edn, x))
                x = f.read(bits)
        #return np.array(data)
        for tup in data:
            donor_data.append(float(tup[0]))
            acceptor_data.append(float(tup[1]))
    FRET_data_obj = FRET_data(donor_data, acceptor_data)
    return FRET_data_obj

def _fit_gauss(bin_centres, frequencies, p0=[1.0, 0.0, 1.0]):
    """
    Fit a histogram with a single gaussian distribution.

    Arguments:

    * bin_centres: list of histogram bin centres
    * frequencies: list of histogram bin frequencies

    Keyword arguments:

    p0: initial values for gaussian fit as a list of floats: [Area, mu, sigma]. (Default: [1.0, 0.0, 1.0])
    """
    def gauss(x, *p):
        A, mu, sigma = p
        return A*np.exp(-(x-mu)**2/(2.*sigma**2))
    coeff, var_matrix = curve_fit(gauss, bin_centres, frequencies, p0)
    hist_fit = gauss(bin_centres, *coeff)
    return coeff, var_matrix, hist_fit


if __name__ == "__main__":
    pass