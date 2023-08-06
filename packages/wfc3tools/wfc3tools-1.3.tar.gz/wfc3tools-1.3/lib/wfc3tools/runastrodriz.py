#!/usr/bin/env python
from __future__ import division # confidence high

""" runastrodriz is a module to control operation of astrodrizzle which removes distortion and combines HST images in the pipeline.
"""
#*** INITIAL VERSION
#W.J. Hack  12 Aug 2011: Initial version based on Version 1.2.0 of
#                        STSDAS$pkg/hst_calib/wfc3/runwf3driz.py
#W.J. Hack  27 Jun 2012: Implement support to process in different directory
#
#W.J. Hack  24 Aug 2012: Provided interface for in-memory option
#
#W.J. Hack  26 Nov 2012: Option to write out headerlets added and debugged


# Import standard Python modules
import os, sys, string,time, shutil
import glob

from stsci.tools import fileutil, asnutil

# Import local modules
import pyfits

try:
    from stsci.tools import teal
except:
    teal = None


# Local variables
__taskname__="runastrodriz"
__version__ = "1.5.1"
__vdate__ = "(26-Nov-2012)"

# Define parameters which need to be set specifically for
#    pipeline use of astrodrizzle
pipeline_pars = {'mdriztab':True,
                 'stepsize':10,
                 'output':'',
                 'updatewcs':True,
                 'preserve':False,
                 'resetbits':4096}

#default marker for trailer files
__trlmarker__ = '*** astrodrizzle Processing Version '+__version__+__vdate__+'***\n'

# History:
# Version 1.0.0 - Derived from v1.2.0 of wfc3.runwf3driz to run astrodrizzle

#### TEAL Interfaces
def help(file=None):
    helpstr = getHelpAsString(docstring=True)
    if file is None:
        print helpstr
    else:
        if os.path.exists(file): os.remove(file)
        f = open(file,mode='w')
        f.write(helpstr)
        f.close()
    

def getHelpAsString(docstring=False):
    """
    Returns documentation on the 'calwf3' function. Required by TEAL.

    return useful help from a file in the script directory called
    __taskname__.help

    """

    install_dir = os.path.dirname(__file__)
    htmlfile = os.path.join(install_dir, 'htmlhelp', __taskname__ + '.html')
    helpfile = os.path.join(install_dir, __taskname__ + '.help')
    if docstring or (not docstring and not os.path.exists(htmlfile)):
        helpString = ' '.join([__taskname__, 'Version', __version__,
                               ' updated on ', __vdate__]) + '\n\n'
        if os.path.exists(helpfile):
            helpString += teal.getHelpFileAsString(__taskname__, __file__)
    else:
        helpString = 'file://' + htmlfile

    return helpString
        

def run(configobj=None):
    process(configobj['input'],force=configobj['force'],
                newpath=configobj['newpath'],inmemory=configobj['in_memory'],
                num_cores=configobj['num_cores'],headerlets=configobj['headerlets'])

#### Primary user interface
def process(inFile,force=False,newpath=None, inmemory=False, num_cores=None,
            headerlets=True):
    """ Run astrodrizzle on input file/ASN table
        using default values for astrodrizzle parameters.
    """
    # We only need to import this package if a user run the task
    import drizzlepac
    from drizzlepac import processInput # used for creating new ASNs for _flc inputs
    import stwcs

    if headerlets:
        from stwcs.wcsutil import headerlet

    # Open the input file
    try:
        # Make sure given filename is complete and exists...
        inFilename = fileutil.buildRootname(inFile,ext=['.fits'])
        if not os.path.exists(inFilename):
            print "ERROR: Input file - %s - does not exist." % inFilename
            return
    except TypeError:
        print "ERROR: Inappropriate input file."
        return

    #If newpath was specified, move all files to that directory for processing
    if newpath:
        orig_processing_dir = os.getcwd()
        new_processing_dir = _createWorkingDir(newpath,inFilename)
        _copyToNewWorkingDir(new_processing_dir,inFilename)
        os.chdir(new_processing_dir)

    # Initialize for later use...
    _mname = None
    _new_asn = None
    _calfiles = []

    # Check input file to see if [DRIZ/DITH]CORR is set to PERFORM
    if '_asn' in inFilename:
        # We are working with an ASN table.
        # Use asnutil code to extract filename
        inFilename = _lowerAsn(inFilename)
        _new_asn = [inFilename]
        _asndict = asnutil.readASNTable(inFilename,None,prodonly=False)
        _fname = fileutil.buildRootname(string.lower(_asndict['output']),ext=['_drz.fits'])
        _cal_prodname = string.lower(_asndict['output'])

        # Retrieve the first member's rootname for possible use later
        _fimg = pyfits.open(inFilename)
        for name in _fimg[1].data.field('MEMNAME'):
            if name[-1] != '*':
                _mname = string.lower(string.split(name,'\0',1)[0])
                break
        _fimg.close()
        del _fimg

    else:
        # Check to see if input is a _RAW file
        # If it is, strip off the _raw.fits extension...
        _indx = string.find(inFilename,'_raw')
        if _indx < 0: _indx = len(inFilename)
        # ... and build the CALXXX product rootname.
        _mname = fileutil.buildRootname(inFilename[:_indx])
        _cal_prodname = inFilename[:_indx]
        # Reset inFilename to correspond to appropriate input for
        # drizzle: calibrated product name.
        inFilename = _mname

        if _mname == None:
            errorMsg = 'Could not find calibrated product!'
            raise Exception,errorMsg

    # Create trailer filenames based on ASN output filename or
    # on input name for single exposures
    if '_raw' in inFile:
        # Output trailer file to RAW file's trailer
        _trlroot = inFile[:inFile.find('_raw')]
    elif '_asn' in inFile:
        # Output trailer file to ASN file's trailer, not product's trailer
        _trlroot = inFile[:inFile.find('_asn')]
    else:
        # Default: trim off last suffix of input filename
        # and replacing with .tra
        _indx = inFile.rfind('_')
        if _indx > 0:
            _trlroot = inFile[:_indx]
        else:
            _trlroot = inFile

    _trlfile = _trlroot + '.tra'

    # Open product and read keyword value
    # Check to see if product already exists...
    dkey = 'DRIZCORR'
    # ...if product does NOT exist, interrogate input file
    # to find out whether 'dcorr' has been set to PERFORM
    # Check if user wants to process again regardless of DRIZCORR keyword value
    if force: dcorr = 'PERFORM'
    else:
        if _mname :
            _fimg = pyfits.open(fileutil.buildRootname(_mname,ext=['_raw.fits']))
            _phdr = _fimg['PRIMARY'].header
            if dkey in _phdr:
                dcorr = _phdr[dkey]
            else:
                dcorr = None
            _fimg.close()
            del _fimg
        else:
            dcorr = None

    time_str = _getTime()
    _tmptrl = _trlroot + '_tmp.tra'
    _drizfile = _trlroot + '_pydriz'
    _drizlog = _drizfile + ".log" # the '.log' gets added automatically by astrodrizzle
    if dcorr == 'PERFORM':
        if '_asn.fits' not in inFilename:
            # Working with a singleton
            # However, we always want to make sure we always use
            # a calibrated product as input, if available.
            _infile = fileutil.buildRootname(_cal_prodname)
            _infile_flc = fileutil.buildRootname(_cal_prodname,ext=['_flc.fits'])

            _cal_prodname = _infile
            _inlist = _calfiles = [_infile]

            # Add CTE corrected filename as additional input if present
            if os.path.exists(_infile_flc) and _infile_flc != _infile:
                _inlist.append(_infile_flc)

        else:
            # Working with an ASN table...
            _infile = inFilename
            flist,duplist = processInput.checkForDuplicateInputs(_asndict['order'])
            _calfiles = flist
            if len(duplist) > 0:
                origasn = processInput.changeSuffixinASN(inFilename,'flt')
                dupasn = processInput.changeSuffixinASN(inFilename,'flc')
                _inlist = [origasn,dupasn]
            else:
                _inlist = [_infile]
            # We want to keep the original specification of the calibration
            # product name, though, not a lower-case version...
            _cal_prodname = inFilename
            _new_asn.extend(_inlist) # kept so we can delete it when finished


        # Run astrodrizzle and send its processing statements to _trlfile
        _pyver = drizzlepac.astrodrizzle.__version__

        for _infile in _inlist: # Run astrodrizzle for all inputs
            # Create trailer marker message for start of astrodrizzle processing
            _trlmsg = _timestamp('astrodrizzle started ')
            _trlmsg = _trlmsg+ __trlmarker__
            _trlmsg = _trlmsg + '%s: Processing %s with astrodrizzle Version %s\n' % (time_str,_infile,_pyver)
            print _trlmsg

            # Write out trailer comments to trailer file...
            ftmp = open(_tmptrl,'w')
            ftmp.writelines(_trlmsg)
            ftmp.close()
            _appendTrlFile(_trlfile,_tmptrl)

            _pyd_err = _trlroot+'_pydriz.stderr'

            try:
                b = drizzlepac.astrodrizzle.AstroDrizzle(input=_infile,runfile=_drizfile,
                                            configobj='defaults',in_memory=inmemory,
                                            num_cores=num_cores, **pipeline_pars)
            except Exception, errorobj:
                _appendTrlFile(_trlfile,_drizlog)
                _appendTrlFile(_trlfile,_pyd_err)
                _ftrl = open(_trlfile,'a')
                _ftrl.write('ERROR: Could not complete astrodrizzle processing of %s.\n' % _infile)
                _ftrl.write(str(sys.exc_type)+': ')
                _ftrl.writelines(str(errorobj))
                _ftrl.write('\n')
                _ftrl.close()
                print 'ERROR: Could not complete astrodrizzle processing of %s.' % _infile
                raise Exception, str(errorobj)

            # Now, append comments created by PyDrizzle to CALXXX trailer file
            print 'Updating trailer file %s with astrodrizzle comments.' % _trlfile
            _appendTrlFile(_trlfile,_drizlog)

        # Save this for when PyFITS can modify a file 'in-place'
        # Update calibration switch
        _fimg = pyfits.open(_cal_prodname,mode='update')
        _fimg['PRIMARY'].header.update(dkey,'COMPLETE')
        _fimg.close()
        del _fimg

        # Enforce pipeline convention of all lower-case product
        # names
        _prodlist = glob.glob('*drz.fits')
        for _prodname in _prodlist:
            _plower = _prodname.lower()
            if _prodname != _plower:  os.rename(_prodname,_plower)

    else:
        # Create default trailer file messages when astrodrizzle is not
        # run on a file.  This will typically apply only to BIAS,DARK
        # and other reference images.
        # Start by building up the message...
        _trlmsg = _timestamp('astrodrizzle skipped ')
        _trlmsg = _trlmsg + __trlmarker__
        _trlmsg = _trlmsg + '%s: astrodrizzle processing not requested for %s.\n' % (time_str,inFilename)
        _trlmsg = _trlmsg + '       astrodrizzle will not be run at this time.\n'
        print _trlmsg

        # Write message out to temp file and append it to full trailer file
        ftmp = open(_tmptrl,'w')
        ftmp.writelines(_trlmsg)
        ftmp.close()
        _appendTrlFile(_trlfile,_tmptrl)

    _fmsg = None
    # Append final timestamp to trailer file...
    _final_msg = '%s: Finished processing %s \n' % (time_str,inFilename)
    _final_msg += _timestamp('astrodrizzle completed ')
    _trlmsg += _final_msg
    ftmp = open(_tmptrl,'w')
    ftmp.writelines(_trlmsg)
    ftmp.close()
    _appendTrlFile(_trlfile,_tmptrl)

    # If we created a new ASN table, we need to remove it
    if _new_asn != None:
        for _name in _new_asn: fileutil.removeFile(_name)

    # Clean up any generated OrIg_files directory
    if os.path.exists("OrIg_files"):
        # check to see whether this directory is empty
        flist = glob.glob('OrIg_files/*.fits')
        if len(flist) == 0:
            os.rmdir("OrIg_files")
        else:
            print 'OrIg_files directory NOT removed as it still contained images...'
    if headerlets:
        # Generate headerlets for each updated FLT image
        hlet_msg = _timestamp("Writing Headerlets started")
        for fname in _calfiles:
            headerlet.write_headerlet(fname,'OPUS',output='flt', wcskey='PRIMARY',
                author="OPUS",descrip="Default WCS from Pipeline Calibration",
                attach=False,clobber=True,logging=False)
            # update trailer file to log creation of headerlet files
            frootname = fileutil.buildNewRootname(fname)
            hname = "%s_flt_hlet.fits"%frootname
            hlet_msg += "Created Headerlet file %s \n"%hname
        hlet_msg += _timestamp("Writing Headerlets completed")
        ftrl = open(_trlfile,'a')
        ftrl.write(hlet_msg)
        ftrl.close()

    # If processing was done in a temp working dir, restore results to original
    # processing directory, return to original working dir and remove temp dir
    if newpath:
        _restoreResults(new_processing_dir,orig_processing_dir)
        os.chdir(orig_processing_dir)
        _removeWorkingDir(new_processing_dir)

    # Provide feedback to user
    print _final_msg


def _lowerAsn(asnfile):
    """ Create a copy of the original asn file and change
        the case of all members to lower-case.
    """
    # Start by creating a new name for the ASN table
    _indx = asnfile.find('_asn.fits')
    _new_asn = asnfile[:_indx]+'_pipeline'+asnfile[_indx:]
    if os.path.exists(_new_asn) == True:
        os.remove(_new_asn)
    # copy original ASN table to new table
    shutil.copy(asnfile,_new_asn)

    # Open up the new copy and convert all MEMNAME's to lower-case
    fasn = pyfits.open(_new_asn,'update')
    for i in xrange(len(fasn[1].data)):
        fasn[1].data[i].setfield('MEMNAME',fasn[1].data[i].field('MEMNAME').lower())
    fasn.close()

    return _new_asn

def _appendTrlFile(trlfile,drizfile):
    """ Append drizfile to already existing trlfile from CALXXX.
    """
    if not os.path.exists(drizfile):
        return
    # Open already existing CALWF3 trailer file for appending
    ftrl = open(trlfile,'a')
    # Open astrodrizzle trailer file
    fdriz = open(drizfile)

    # Read in drizzle comments
    _dlines = fdriz.readlines()

    # Append them to CALWF3 trailer file
    ftrl.writelines(_dlines)

    # Close all files
    ftrl.close()
    fdriz.close()

    # Now, clean up astrodrizzle trailer file
    os.remove(drizfile)


def _timestamp(_process_name):
    """Create formatted time string recognizable by OPUS."""
    _prefix= time.strftime("%Y%j%H%M%S-I-----",time.localtime())
    _lenstr = 60 - len(_process_name)
    return _prefix+_process_name+(_lenstr*'-')+'\n'

def _getTime():
    # Format time values for keywords IRAF-TLM, and DATE
    _ltime = time.localtime(time.time())
    time_str = time.strftime('%H:%M:%S (%d-%b-%Y)',_ltime)

    return time_str

#### Functions used to manage processing in a separate directory/ramdisk
def _createWorkingDir(rootdir,input):
    """
    Create a working directory based on input name under the parent directory specified as rootdir
    """
    # extract rootname from input
    rootname = input[:input.find('_')]
    newdir = os.path.join(rootdir,rootname)
    if not os.path.exists(newdir):
        os.mkdir(newdir)
    return newdir

def _copyToNewWorkingDir(newdir,input):
    """ Copy input file and all related files necessary for processing to the new working directory.

        This function works in a greedy manner, in that all files associated
        with all inputs(have the same rootname) will be copied to the new
        working directory.
    """
    flist = []
    if '_asn.fits' in input:
        asndict = asnutil.readASNTable(input,None)
        flist.append(input[:input.find('_')])
        flist.extend(asndict['order'])
        flist.append(asndict['output'])
    else:
        flist.append(input[:input.find('_')])
    # copy all files related to these rootnames into new dir
    for rootname in flist:
        for fname in glob.glob(rootname+'*'):
            shutil.copy(fname,os.path.join(newdir,fname))

def _restoreResults(newdir,origdir):
    """ Move (not copy) all files from newdir back to the original directory
    """
    for fname in glob.glob(os.path.join(newdir,'*')):
        shutil.move(fname,os.path.join(origdir,os.path.basename(fname)))

def _removeWorkingDir(newdir):
    """ Delete working directory
    """
    os.rmdir(newdir)

process.__doc__ = getHelpAsString(docstring=True)

#### Functions to support execution from the shell.
def main():

    import getopt

    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'bhfin:')
    except getopt.error, e:
        print str(e)
        print __doc__
        print "\t", __version__

    # initialize default values
    help = 0
    force = False
    newdir = None
    inmemory = False
    num_cores = None
    headerlets= True

    # read options
    for opt, value in optlist:
        if opt == "-h":
            help = 1
        if opt == "-f":
            force = True
        if opt == "-i":
            inmemory = True
        if opt == '-n':
            if not value.isdigit():
                print 'ERROR: num_cores value must be an integer!'
                raise ValueError
            num_cores = int(value)
        if opt == '-b':
            # turn off writing headerlets
            headerlets=False
    if len(args) < 1:
        print "syntax: runastrodriz.py [-fhibn] inputFilename [newpath]"
        sys.exit()
    if len(args) > 1:
        newdir = args[-1]
    if (help):
        print __doc__
        print "\t", __version__+'('+__vdate__+')'
    else:
        try:
            process(args[0],force=force,newpath=newdir, inmemory=inmemory,
                    num_cores=num_cores, headerlets=headerlets)
        except Exception, errorobj:
            print str(errorobj)
            print "ERROR: Cannot run astrodrizzle on %s." % sys.argv[1]
            raise Exception, str(errorobj)

    sys.exit()

if __name__ == "__main__":
    main()
