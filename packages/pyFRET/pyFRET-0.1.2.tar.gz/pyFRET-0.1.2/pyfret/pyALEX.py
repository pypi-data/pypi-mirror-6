import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import os
import sys
import struct
import matplotlib
from matplotlib.ticker import NullFormatter
from scipy.optimize import curve_fit
import csv

class ALEX_data:

    """
    This class holds single molecule data.

    It has four attributes, corresponding to the four photon streams from an ALEX experiment. These are numpy arrays:

    * D_D: Donor channel when the donor laser is on
    * D_A: Donor channel when the acceptor laser is on
    * A_D: Acceptor channel when the donor laser is on
    * A_A: Acceptor channel when the acceptor laser is on    

    It can be initialized from four lists or four arrays of photon counts: data = FRET_data(D_D_events, D_A_events, A_D_events, A_A_events)

    """

    def __init__(self, D_D, D_A, A_D, A_A):
        """
        Initialize the ALEX_data object.

        Arguments:

        * D_D: Donor channel when the donor laser is on
        * D_A: Donor channel when the acceptor laser is on
        * A_D: Acceptor channel when the donor laser is on
        * A_A: Acceptor channel when the acceptor laser is on  

        """
        self.D_D = np.array(D_D).astype(float)
        self.D_A = np.array(D_A).astype(float)
        self.A_D = np.array(A_D).astype(float)
        self.A_A = np.array(A_A).astype(float)

    def subtract_bckd(self, bckd_D_D, bckd_D_A, bckd_A_D, bckd_A_A):
        """
        Subtract background noise from the four data channels.

        Arguments:

        * bckd_D_D: average noise per time-bin in the channel D_D
        * bckd_D_A: average noise per time-bin in the channel D_A
        * bckd_A_D: average noise per time-bin in the channel A_D
        * bckd_A_A: average noise per time-bin in the channel A_A
        """
        self.D_D = self.D_D - bckd_D_D
        self.D_A = self.D_A - bckd_D_A
        self.A_D = self.A_D - bckd_A_D
        self.A_A = self.A_A - bckd_A_A
        return self

    def thresholder(self, T_D, T_A):
        """
        Select events that have photons above a threshold.

        Arguments:

        * T_D: threshold for photons during donor laser excitation
        * T_A: threshold for photons during acceptor laser excitation

        An event is above threshold if nA_D + nD_D > T_D AND nA_A > T_A
        for nA_D, nD_D and nA_A photons in the channels A_D, D_D and A_A respectively
        """
        select = ((self.D_D + self.A_D > T_D) & (self.A_A > T_A))
        self.D_D = self.D_D[select]
        self.D_A = self.D_A[select]
        self.A_D = self.A_D[select]
        self.A_A = self.A_A[select]
        return self

    def stoichiometry_selection(self, S, S_min, S_max):
        """
        Select data with photons above a threshold.

        Arguments:

        * S: array of stoichiometry values calculated using the stoichiometry method
        * S_min: minimum accepted value of S (float)
        * S_max: maximum accepted value of S (float)

        Event selection criterion: Smin < Sx < Smax, for Stoichiometry Sx of event x
        """
        select = ((S > S_min) & (S < S_max))
        self.D_D = self.D_D[select]
        self.D_A = self.D_A[select]
        self.A_D = self.A_D[select]
        self.A_A = self.A_A[select]
        S = S[select]
        return S

    def subtract_crosstalk(self, l, d):
        """
        Subtract crosstalk from the FRET channel A_D

        Arguments:

        * l: leakage constant from donor channel D_D to acceptor channel A_D (float between 0 and 1)
        * d: direct excitation of the acceptor by the donor laser (float between 0 and 1)
        """
        lk = l * self.D_D
        dire = d * self.A_A
        self.A_D = self.A_D - (lk + dire)
        return self

    def proximity_ratio(self, gamma=1.0):
        """
        Calculate the proximity ratio (E) and return an array of values.

        Arguments:
        None    

        Keyword arguments:
        gamma (default value 1.0): the instrumental gamma-factor

        Calculation: 
        E = nA / (nA + gamma*nD) 
        for nA and nD photons in the acceptor (A_D) and donor (D_D) channels respectively
        """
        E = self.A_D / (self.D_D + (gamma * self.A_D))
        return E

        
    def stoichiometry(self, gamma=1.0):
        """
        Calculate the stoichiometry (S) and return an array of values.

        Arguments:
        None    

        Keyword arguments:
        gamma (default value 1.0): the instrumental gamma-factor

        Calculation: 
        S = (gamma*D_D + A_D) / (gamma*D_D + A_D + A_A)
        """
        num = gamma*self.D_D + self.A_D
        denom = gamma*self.D_D + self.A_D + self.A_A
        S = num / denom
        return S

    def scatter_hist(self, S_min, S_max, gamma=1.0, save=False, filepath=None, imgname=None, imgtype=None):
        """
        Plot a scatter plot of E (proximity ratio) vs S (stoichiometry) and projections of selected E and S values

        Arguments:

        * S_min: minimum accepted value of S (float between 0 and 1)
        * S_max: maximum accepted value of S (float between 0 and 1)

        Keyword arguments:

        * gamma: Instrumental gamma factor. (float, default value 1.0)
        * save: Boolean. True will save an image of the graph plotted (default False)
        * filepath: file path to the directory in which the image will be saved (default None)
        * imgname: name under which the image will be saved (default None)
        * imgtype: filetype of histogram image. Accepted values: jpg, tiff, rgba, png, ps, svg, eps, pdf
        """
        # Eraw, Sraw, Eclean, Sclean, 
        # get rough values (pre thresholding)
        Eraw = self.proximity_ratio(gamma)
        Sraw = self.stoichiometry(gamma)
        x1 = Eraw
        y1 = Sraw

        # select based on threshold
        self.stoichiometry_selection(Sraw, S_min, S_max)

        # recalculate E and S
        Eclean = self.proximity_ratio()
        Sclean = self.stoichiometry()
        x2 = Eclean
        y2 = Sclean

        # prepare plot
        nullfmt   = NullFormatter()         # no labels

        # definitions for the axes
        left, width = 0.1, 0.65
        bottom, height = 0.1, 0.65
        bottom_h = left_h = left+width+0.02

        rect_scatter = [left, bottom, width, height]
        rect_histx = [left, bottom_h, width, 0.2]
        rect_histy = [left_h, bottom, 0.2, height]

        # start with a rectangular Figure
        plt.figure(1, figsize=(8,8))

        axScatter = plt.axes(rect_scatter)
        plt.xlabel("E")
        plt.ylabel("S")
        axHistx = plt.axes(rect_histx)
        plt.ylabel("Frequency")
        axHisty = plt.axes(rect_histy)
        plt.xlabel("Frequency")

        # no labels
        axHistx.xaxis.set_major_formatter(nullfmt)
        axHisty.yaxis.set_major_formatter(nullfmt)

        # the scatter plot:
        axScatter.scatter(x1, y1)
        axScatter.axhline(S_min, c="r", ls="--")
        axScatter.axhline(S_max, c="r", ls="--")

        

        # now determine nice limits by hand:
        binwidth = 0.02
        xymax = np.max( [np.max(np.fabs(x1)), np.max(np.fabs(y1))] )
        lim = ( int(xymax/binwidth) + 1) * binwidth

        axScatter.set_xlim( (-lim, lim) )
        axScatter.set_ylim( (-lim, lim) )
        axScatter.set_xlim( (0.0, 1.0) )
        axScatter.set_ylim( (0.0, 1.0) )

        bins = np.arange(0.0, 1.0 + binwidth, binwidth)
        axHistx.hist(x1, bins=bins)
        axHistx.locator_params(nbins=4)
        axHisty.hist(y1, bins=bins, orientation='horizontal')
        axHisty.locator_params(nbins=4)

        axHistx.set_xlim( axScatter.get_xlim() )
        axHisty.set_ylim( axScatter.get_ylim() ) 
        if save and not imgname == None and not filepath == None and not imgtype == None: 
            picname = ".".join([imgname, imgtype])
            picpath = os.path.join(filepath, picname)  
            plt.savefig(picpath)
        plt.clf()
        plt.cla()
        return self

    def build_histogram(self, filepath, csvname, gamma=1.0, bin_min=0.0, bin_max=1.0, bin_width=0.02, image = False, imgname = None, imgtype=None, gauss = False, gaussname = None):
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
        * bin-width: the width of one bin (default 0.02)
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
            csv_file.close()
        plt.clf()
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
    "D_D,D_A,A_D,A_A\n" 

    If your data does not have this format (for example if you have separate files for donor and acceptor data), this function will not work well for you.
    
    """
    D_D = []
    D_A = []
    A_D = []
    A_A = []
    for fp in filelist:
        current_file = os.path.join(filepath, fp)
        with open(current_file) as csv_file:
            current_data = csv.reader(csv_file, delimiter=',')
            for row in current_data:
                D_D.append(float(row[0]))
                D_A.append(float(row[1]))
                A_D.append(float(row[2]))
                A_A.append(float(row[3]))
    ALEX_data_obj = ALEX_data(D_D, D_A, A_D, A_A)
    return ALEX_data_obj


def parse_bin(filepath, filelist, bits=16):
    """
    Read data from a list of binary files and return an ALEX_data object.

    Arguments:
    * filepath: the path to the folder containing the files
    * filelist: list of files to be analysed

    Keyword arguments:
    * bits (default value 16): the number of bits used to store a donor-acceptor pair of time-bins 

    **Note: This file structure is probably specific to the Klenerman group's .dat files.**
        **Please don't use it unless you know you have the same filetype!**
    """
    # note that this makes several assumptions about the file structure
    # which are hard-coded. This is pretty ugly and should be changed
    byte_order = sys.byteorder
    try:
        if byte_order == "little":
            edn = '>ii'
        elif byte_order == "big":
            edn = '<ii'
    except ValueError:
        print "Unknown byte order"
        raise
    D_D = []
    D_A = []
    A_D = []
    A_A = []

    for fp in filelist:
        current_file = os.path.join(filepath, fp)
        counter = 0
        data = []
        with open(current_file, "rb") as f:
            x = f.read(bits)
            while x:
                data.append((struct.unpack(edn, x[:8]), struct.unpack(edn, x[8:])))
                x = f.read(bits)
        for tup in data:
            #print tup
            D_D.append(float(tup[0][0]))
            D_A.append(float(tup[0][1]))
            A_D.append(float(tup[1][0]))
            A_A.append(float(tup[1][1]))
    ALEX_data_obj = ALEX_data(D_D, D_A, A_D, A_A)
    return ALEX_data_obj


def _fit_gauss(bin_centres, frequencies, p0=[1.0, 0.0, 1.0]):
    """
    Fit a histogram with a single gaussian distribution.

    Arguments:
    * bin_centres: list of histogram bin centres
    * frequencies: list of histogram bin frequencies

    Keyword arguments:
    * p0: initial values for gaussian fit as a list of floats: [Area, mu, sigma]. (Default: [1.0, 0.0, 1.0])
    """
    def gauss(x, *p):
        A, mu, sigma = p
        return A*np.exp(-(x-mu)**2/(2.*sigma**2))
    coeff, var_matrix = curve_fit(gauss, bin_centres, frequencies, p0)
    hist_fit = gauss(bin_centres, *coeff)
    return coeff, var_matrix, hist_fit


