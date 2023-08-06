from __future__ import division, print_function # confidence high

#get the auto update version 
from .version import *
from .sub2full import sub2full

# STDLIB
import pyfits
import os
import numpy

#STSCI
from stsci.tools import parseinput
from stsci.tools import teal

__taskname__ = "embedsub"
__vdate__ = "10-Jan-2014"

def embedsub(files):
    """Return the full-frame location of the subarray coordinates using a  file specified by the user. 
    
    Parameters
    ----------
    filename : string
       The name of the image file containing the subarray. This can be a single filename or a list of files.
       The ippsoot will be used to construct the output filename. You should input an FLT image

    The output file will contain the subarray image placed inside the full frame extent of a regular image

    """
    uvis=False
    uvis_full_x = 2051
    uvis_full_y = 4096
    ir_full = 1014
    
    infiles, dummy_out= parseinput.parseinput(files)
    if len(infiles) < 1:
        return ValueError("Please input a valid HST filename")

    #process all the input subarrays
    for filename in infiles:
    
        # Make sure the input name conforms to normal style
        if '_flt' not in filename:
           print ("Warning: Can't properly parse '%s'; Skipping" % file)

        # Extract the root name and build SPT and output file names
        root = filename[0:filename.find('_flt')]
        spt = root + '_spt.fits'
        full = root[0:len(root)-1] + 'f_flt.fits'

        try:
            flt=pyfits.open(filename)
        except EnvironmentError:
            print("Problem opening fits file %s"%(filename))
            
        detector=flt[0].header['DETECTOR']
        if 'UVIS' in detector:
            uvis=True
            
                    
        #compute subarray corners assuming the raw image location
        x1,x2,y1,y2=sub2full(filename,fullExtent=True)[0]
        print("Subarray image section [x1,x2,y1,y2] = [%d:%d,%d:%d]"%(x1,x2,y1,y2))

        if uvis:
            xaxis=uvis_full_x
            yaxis=uvis_full_y
        else:
            xaxis=ir_full
            yaxis=ir_full
            
        # Now copy the subarray image data into full-chip data arrays;
        # The regions outside the subarray will be set to zero in the
        # SCI, ERR, SAMP, and TIME extensions, and to DQ=4.
        sci = numpy.zeros([xaxis,yaxis],dtype=numpy.float32)
        err = numpy.zeros([xaxis,yaxis],dtype=numpy.float32)
        dq  = numpy.zeros([xaxis,yaxis],dtype=numpy.int16) + 4

       
        sci[y1-1:y2,x1-1:x2] = flt[1].data
        err[y1-1:y2,x1-1:x2] = flt[2].data
        dq[y1-1:y2,x1-1:x2]  = flt[3].data
    
        if not uvis:
            samp = numpy.zeros([xaxis,yaxis],dtype=numpy.int16)
            time = numpy.zeros([xaxis,yaxis],dtype=numpy.float32)
            samp[y1-1:y2,x1-1:x2] = flt[4].data
            time[y1-1:y2,x1-1:x2] = flt[5].data

    

        # Reset a few WCS values to make them appropriate for a
        # full-chip image
        crpix1=flt[1].header['CRPIX1']
        crpix2=flt[1].header['CRPIX2']
        
        flt[1].header['sizaxis1'] = yaxis
        flt[1].header['sizaxis2'] = xaxis
        
        for i in range(1,4):
            flt[i].header['crpix1'] = crpix1 + x1 - 1
            flt[i].header['crpix2'] = crpix2 + y1 - 1
            flt[i].header['ltv1']   = 0.0
            flt[i].header['ltv2']   = 0.0

        #set the header value of SUBARRAY to False since it's now  regular size image
        flt[0].header['SUBARRAY']=False
        
        # Now write out the SCI, ERR, DQ extensions to the full-chip file
        hdulist=pyfits.HDUList()
        hdulist.append(pyfits.ImageHDU(flt[0].data,header=flt[0].header))
        hdulist.append(pyfits.ImageHDU(sci,header=flt[1].header,name='SCI'))
        hdulist.append(pyfits.ImageHDU(err,header=flt[2].header,name='ERR'))
        hdulist.append(pyfits.ImageHDU(dq,header=flt[3].header,name='DQ'))
                
        if not uvis:
           hdulist.append(pyfits.ImageHDU(dq,header=flt[4].header,name='SAMP'))
           hdulist.append(pyfits.ImageHDU(dq,header=flt[5].header,name='TIME'))

        hdulist.writeto(full,clobber=False)
       
        # close the input files
        flt.close()
        print("Image saved to: %s"%(full))
        

def getHelpAsString(docstring=False):
    """
    Returns documentation on the 'embedsub' function.

    return useful help from a file in the script directory called
    __taskname__.help

    """

    install_dir = os.path.dirname(__file__)   
    helpfile = os.path.join(install_dir, __taskname__ + '.help')
    
    if docstring or (not docstring):
        helpString = ' '.join([__taskname__, 'Version', __version__,
                               ' updated on ', __vdate__]) + '\n\n'
    if os.path.exists(helpfile):
            helpString += teal.getHelpFileAsString(__taskname__, __file__)
        
    return helpString
        
    
def help():
    print(getHelpAsString(docstring=True))

__doc__ = getHelpAsString(docstring=True)

if __name__ == "main":
    """called as a function from the terminal just return the default corner locations """
    import sys
    embedsub(sys.argv[1])
