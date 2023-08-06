## Automatically adapted for numpy.numarray Feb 05, 2007 by

"""
saaclean: Module for estimating and removing persistent CR signal due to a prior
          SAA passage.

:Usage:    Normally used via the STSDAS task saaclean in the nicmos package.
          To use as pure python, create a params object to override any of
          the default parameters if desired, then invoke clean::

            >>> mypars=saaclean.params(thresh=0.23)
            >>> saaclean.clean('inputfile.fits','outputfile.fits',pars=mypars)

:For more information:
          Additional user information, including parameter definitions and more
          examples, can be found in the help file for the STSDAS saaclean task,
          located in nicmos$doc/saaclean.hlp.

          The algorithm and IDL prototype are described in the NICMOS
          ISR 2003-009, by Bergeron and Dickinson, available through the NICMOS
          webpage.

:Dependencies:
  - numpy 1.0.2.dev3534 or higher
  - pyfits v1.1b4 or higher
  - imagestats v1.3 or higher

"""

from __future__ import division

__version__="1.4"
__vdate__="2010-10-20"

# The above text is duplicated in the __init__ file for the package, since
#that's where it shows up for the user.
from stsci.tools import numerixenv #Temporary NUMERIX environment check
from stsci.tools import fileutil
import os
import exceptions
import numpy as N, pyfits
from stsci.imagestats import ImageStats as imstat #pyssg lib
from stsci.imagestats.histogram1d import histogram1d
import SP_LeastSquares as LeastSquares #Excerpt from Hinsen's Scientific Python
from numpy.linalg import LinAlgError

#History:
# New version of imagestats: 14 Dec 09, Laidler
#   - imagestats v1.3 uses "midpt" to duplicate iraf imstats functionality
# Enhancements, 20 Jan 06, Laidler
#   - replaced infile by calcfile and targfile
#   - allow applying correction to a file other than that on which it
#     was computed
#   - added "clobber" parameter to control clobber behavior on all
#     output files.
# Enhancement, 21 Dec 05, Laidler
#  use header value of ADCGAIN in place of GAINPLOT
#  add new CRTHRESH, NOISETHRESH, BINSIGFRAC parameters
# Enhancement, 21 Dec 05, Laidler
#    - add chi2 output to header keyword set. This involved changing
#      the signature of the parabola_min function to return the chi2.
# Enhancement, 19 Dec 05, Laidler
#    - use DQ extension for bad pixels
# Bugfix,21 Jan 05, Laidler
#    - make all paths & filenames more robust via osfn
# Bugfix,20 Jan 05, Laidler:
#    - correct handling of middle column/row in Exposure.pedskyish()
# Bugfixes, 3 Aug 04, Laidler:
#    - make filename construction more robust via os.path.abspath on the directory
#    - Ensure directory specified in pars.darkpath exists
#    - Fall back to extension 0 if extension 1 doesn't exist (Exposure class)
#    - Support noise reduction in high domain only
# Initial python implementation: Dec 2003, Laidler
# Based on IDL implementation by Bergeron

#Notes for future improvement:
# - possibly make saaper its own class
# - the crthreshholding code is kind of tacky
# - possibly make filename its own class so it can have a method for nref
#   instead of using the osfn helper function
#........................................................................
#Class definitions
#.........................................................................

class params:
    def __init__(self,scale=0.54,wf1=0.7,wf2=0.3,
                 stepsize=0.008,thresh=None,hirange=0.4,lorange=0.25,dofit=1,
                 crthresh=0.3, noisethresh=1.0, binsigfrac=0.3,
                 readsaaper='False',writesaaper='True',saaperfile='saaper.fits',
                 fitthresh='True',histbinwidth=0.01, nclip=10,
                 clobber='False',
                 flatsaaper='True',flatsaaperfile=None,
                 maskfile=None,darkpath=None,diagfile=None):
        self.scale=scale
        self.wf1=wf1
        self.wf2=wf2
        self.writesaaper=writesaaper
        self.readsaaper=readsaaper
        self.saaperfile=osfn(saaperfile)
        self.clobber=clobber
        self.flatsaaper=flatsaaper
        self.flatsaaperfile=osfn(flatsaaperfile)
        self.maskfile=osfn(maskfile)
        self.stepsize=stepsize
        self.thresh=thresh
        self.hirange=hirange
        self.lorange=lorange
        self.dofit=dofit

        self.fitthresh=fitthresh
        self.histbinwidth=histbinwidth
        self.nclip=nclip

        self.crthresh=crthresh
        self.noisethresh=noisethresh
        self.binsigfrac=binsigfrac

        self.darkpath=osfn(darkpath)
        self.diagfile=osfn(diagfile)

        self.appstring=None   # Might be needed later.

class Domain:
    """ Stores a list of pixels for a (typically high or low) signal domain"""

    def __init__(self,name,pixellist,range):
        self.name=name
        self.pixlist=pixellist
        self.range=range
        self.npix=len(self.pixlist[0])
        #Because the pixlist is created with a "where" statement, it's a
        #2 element array, 1 for x & 1 for y. Thus to get the number of
        #pixels, we need the length in one of the elements.



    def striplowerthan(self,factor):
        """self.pp is defined in Exposure.getscales
        It contains the (bin, stddev, mode) for the statistical analysis.
        striplowerthan(factor) examines the stddev column only, and replaces
        all values of the stddev that are less than factor*the zeroth bin,
        with the maximum stddev.
        """
        p1=self.pp[1,:]
        uu=N.where(p1 < factor*p1[0])
        if uu[0].size != 0:
            p1[uu]=p1.max()
            self.pp[1,:]=p1

    def getmin(self):
        ubest=N.where(self.pp[1,:] == self.pp[1,:].min())[0][0]
        umode=N.where(self.pp[2,:] == self.pp[2,:].min())[0][0]
        return ubest, umode

    def writeto(self,filename,clobber=False):
        if not clobber:
            if os.path.exists(filename):
                raise IOError, "%s already exists: aborting\n"%filename
        #if clobber=True or file does not exist, proceed anyhow
        f=open(filename,'w')
        f.write('# '+self.name+'\n')
        f.write('# Pixels in this domain: '+`len(self.pixlist[0])`+'\n')
        f.write('#  1  scale factor  \n')
        f.write('#  2  sigma   \n')
        f.write('#  3  mode  \n')
        for i in range(len(self.pp[0])):
            f.write('%f   %f    %f\n' % (self.pp[0,i],self.pp[1,i],self.pp[2,i]))
        f.close()


class Exposure:
    """ Stores a collection of keywords and the image data for an exposure. """

    def __init__(self,imgfile,nickname=None):

        self.filename=osfn(imgfile)
        if nickname is None:
            self.nickname=self.filename
        else:
            self.nickname=nickname
        f=pyfits.open(self.filename)
        self.f=f
        h=f[0].header
        self.h=h
        try: #Assume data is in extension 1. if not, fall back to extension 0.
            self.data=f[1].data   #.astype('Float32')
            self.extnum=1
        except IndexError:
            self.data=f[0].data
            self.extnum=0
        self.exptime=h['exptime']
        self.camera=h['camera']
        self.saa_time=h['saa_time']
        self.badfile=osfn(h['maskfile'])
        self.tdkfile=osfn(h.get('saadfile'))
        self.gainplot=h['adcgain']

        self.inq1=slice(10,118),slice(10,118)
        self.inq2=slice(10+128,118+128),slice(10,118)
        self.inq3=slice(10+128,118+128),slice(10+128,118+128)
        self.inq4=slice(10,118),slice(10+128,118+128)

        self.q1=slice(0,128),slice(0,128)
        self.q2=slice(128,256),slice(0,128)
        self.q3=slice(128,256),slice(128,256)
        self.q4=slice(0,128),slice(128,256)


        print self.nickname, ": using DQ extension for badpix"
        try:
            self.dq=f['dq',1].data
            if self.dq is not None:
                dqmask = 1+16+32+64+128+256 #selected values
                self.nonsourcemask=N.bitwise_and(self.dq, dqmask+1024) #exclude sources
                self.nonsourceidx=N.where(self.nonsourcemask == 0)
                self.nonsource=self.data[self.nonsourceidx]
                self.badpix=N.bitwise_and(self.dq, dqmask)
            else:
                self.badpix=None
        except KeyError,e:
            print e
            print 'DQ extension not found for %s'%imgfile
            print 'defaulting to maskfile'
            self.badpix = None

 #       print "self.badpix.shape = ",self.badpix.shape

        if self.badpix is None:
            print "failing over to ",self.badfile
            try:
                f2=pyfits.open(self.badfile)
                self.badpix=f2['dq',1].data
                f2.close()
            except IOError,e:
                print e
                print "Bad pixel image not read"
                print "Bad pixel image filename obtained from ",self.filename
                self.badpix=None

        #Don't leave file handles hanging around
        self.f.close()

    def writeto(self,outname,clobber=False):
        f=pyfits.open(self.filename)
        f[self.extnum].data=self.data
        f[0].header=self.h #update the primary header
        f.writeto(outname,clobber=clobber)

    def dark_subtract(self,dark):
        self.data=(self.data-dark)/self.exptime


    def pedskyish(self):
        """ Performs something like the IRAF pedsky task, but with a bit more
        sophistication in handling the central row and column"""

        #Compute the median for each quadrant independently
##         m=N.array([imstat(self.data[self.inq1],nclip=0,binwidth=0.01,fields='median').median,
##                           imstat(self.data[self.inq2],nclip=0,binwidth=0.01,fields='median').median,
##                           imstat(self.data[self.inq3],nclip=0,binwidth=0.01,fields='median').median,
##                           imstat(self.data[self.inq4],nclip=0,binwidth=0.01,fields='median').median])

        m=N.array([median(self.data[self.inq1]),
                         median(self.data[self.inq2]),
                         median(self.data[self.inq3]),
                         median(self.data[self.inq4])])
##      print "file ",self.filename
##      print "raw m",m
##      temp=imstat(m,nclip=1,binwidth=0.01,fields='mean,median')
##      print "stats: mean/median",m.mean(),median(m)
        m=m-median(m)
##      print "after sub",m

        #Subtract the median from each quadrant
        self.data[self.q1]=self.data[self.q1]-m[0]
        self.data[self.q2]=self.data[self.q2]-m[1]
        self.data[self.q3]=self.data[self.q3]-m[2]
        self.data[self.q4]=self.data[self.q4]-m[3]


        #"special handling of middle col/row"
        if self.camera < 3:
            temp=imstat( (self.data[:,127]-self.data[:,126]),
                         nclip=1,binwidth=0.01,fields='midpt')
            self.data[:,127]=self.data[:,127]-temp.midpt
        elif self.camera==3:
            temp=imstat( (self.data[127,:]-self.data[126,:]),
                         nclip=1,binwidth=0.01,fields='midpt')
            self.data[127,:]=self.data[127,:]-temp.midpt
        else:
            raise ValueError, "Bad camera value"

##...................................................................................
## Original code that I think is wrong:
##        transcribed parens from idl code incorrectly
##...................................................................................
##         #Camera 3 is special: treat its middle column in a similar way
##         if self.camera < 3:
##             temp=imstat(self.data[:,127],nclip=1,binwidth=0.01,fields='median')
##         #    print "line 127 median is ",temp.median
##         #    print "line 127 mean is ",self.data[:,127].mean()
##             self.data[:,127]=self.data[:,127]-temp.median-self.data[:,126]
##         elif self.camera==3:
##             temp=imstat(self.data[127,:],nclip=1,binwidth=0.01,fields='median')
##             self.data[127,:]=self.data[127,:]-temp.median-self.data[126,:]
##         else:
##             raise ValueError, "Bad camera value"


    def getmask(self,dim=256,border=3,writename='mask.dat',clobber=False):
        """Computes a mask to use for pixels to omit"""
        mask=N.zeros((dim,dim),dtype=N.dtype('float32'))
        badmask=N.ones((dim,dim),dtype=N.dtype('float32'))
        if self.badpix is not None:
            u=N.where(self.badpix != 0)
            mask[u]=1
            badmask[u]=0
        # Always Mask out central "cross" chipgap
        mask[(dim/2)-1,:]=1
        mask[:,(dim/2)-1]=1
        # and the very edges
        mask[0:16,:]=1    #apparently the bottom edge is different
        mask[dim-border:dim,:]=1
        mask[:,0:border+1]=1
        mask[:,dim-border:dim]=1

        if writename:
            writeimage(mask,writename,clobber=clobber)
        return mask,badmask

    def apply_mask(self,mask):
        goodpix=N.where(mask == 0)
        self.masked_data = self.data[goodpix]


    def getscales(self,saaper,mask,pars):

        cal=self.data*self.exptime
        acc=saaper*self.exptime

        for dom in self.domains.values():
            try:
                sz1=int(dom.range/pars.stepsize)+1
                stepval=[pars.stepsize*i for i in xrange(sz1)]

                #there's got to be a better way to do this!
                #Make a mask & fill it all with ones
                fitmask=N.ones(mask.shape)
                #Then make the pixels we want be set to zero
                fitmask[dom.pixlist]=0
                #Then set the mask-defined bad pixels to one so we don't use them
                #(Notice there's no use of "self.badpix" here, wonder why not?)
                #Ah! It's because self.badpix was already used in *making* that mask. OK.
                badpix=N.where(mask == 1)
                fitmask[badpix]=1
                #Finally, choose only those pixels where it's set to zero.
                umask=N.where(fitmask == 0)

                dom.pp=N.zeros((3,int(dom.range/pars.stepsize)+1),dtype=N.dtype('float32'))
                index=0
                for i in stepval:
                    dif=cal-(acc*i)
                    temp=imstat(dif[umask],binwidth=0.01,nclip=3,fields='stddev,mode') #sigma=100
                    dom.pp[:,index]=i,temp.stddev,temp.mode
                    index+=1
                dom.striplowerthan(pars.binsigfrac)
                if pars.diagfile:
                    dom.writeto(pars.diagfile+'_'+dom.name+'_signal_domain.dat',clobber=pars.clobber)
                ubest,umode=dom.getmin()
                best=dom.pp[0,ubest]

                print "\nResults summary for %s domain:"%dom.name
                if pars.dofit:
                    minx=max(ubest-5,0)
                    maxx=min(ubest+5,len(dom.pp[0])-1)
                    thedata=[(dom.pp[0,i],dom.pp[1,i]) for i in range(minx,maxx+1)]

                    best,dom.chi2,itertrace=parabola_min(thedata,best)
                   # best=parabola1(dom.pp[0,minx:maxx],pp[1,minx:maxx],minguess=best)
                   # best=parabola1(dom.pp[0,minx:maxx],pp[1,minx:maxx],minguess=best)

                dom.nr=(1.0-dom.pp[1,ubest]/dom.pp[1,0])*100
                dom.scale=best
                dom.bestloc=ubest


                #print "   zero-mode scale factor is       : ",dom.pp[0,umode]
                print "   min-noise (best) scale factor is: ",dom.scale
                print "   effective noise at this factor (electrons at gain %f): %f"%(self.gainplot,dom.pp[1,ubest]*self.gainplot)
                print "   noise reduction (percent)       : ",dom.nr

                #Apply a sensibility check
                if dom.scale < 0:
                    raise NegScaleError, "ERROR: Best scale factor for %s domain is negative"%dom.name
            except ValueError,e:
                print "Error calculating scale for %s domain"%dom.name
                print str(e)
                print "No correction can be calculated for this domain"
                dom.nr = 0
                dom.scale = 0
                dom.bestloc=0
                dom.chi2=0

    def apply_domains(self,saaper,badmask,noisethresh,appimage=None):
        if appimage is not None:
            final=appimage
        else:
            final=self.data.copy()

        saacorr=N.zeros(final.shape,dtype=N.dtype('float32'))

        hdom,ldom=self.domains['high'],self.domains['low']
        self.update=1
        if hdom.nr >= noisethresh and ldom.nr >= noisethresh:
            print "\n Applying noise reduction in both domains "
            self.appstring='both'
            saacorr[ldom.pixlist]=saaper[ldom.pixlist]*(ldom.scale*badmask[ldom.pixlist])
            saacorr[hdom.pixlist]=saaper[hdom.pixlist]*(hdom.scale*badmask[hdom.pixlist])

        elif hdom.nr > noisethresh and ldom.nr < noisethresh:
            print "\n Applying noise reduction in high domain only "
            self.appstring='high only'
            saacorr[hdom.pixlist]=saaper[hdom.pixlist]*(hdom.scale*badmask[hdom.pixlist])

        elif hdom.nr < noisethresh and ldom.nr >= noisethresh:
            print "\n...Noise reduction in high domain < 1%: applying low scale everywhere"
            self.appstring='low everywhere'
            saacorr=saaper*(ldom.scale*badmask)

        elif hdom.nr < noisethresh and ldom.nr < noisethresh:
            print "\n*** Noise reduction < 1 %, not applying"
            self.appstring='none'
            self.update=0
        else:
            raise ValueError,"Huh?? hi_nr, lo_nr: %f %f"%(hdom.nr,ldom.nr)

        if self.appstring != 'none':
            final=final-saacorr

##         import futil
##         futil.writeimage(saacorr,'scaled_sapper.fits')

        return final

    def update_header(self,pars,tag='default',header=None):
        """ Update the FITS header with all this good stuff we've done"""

        #Start with the last keyword, for ease of applying.

        if header is None:
            header=self.h

        #Describe what was applied
        lastkey='SCNAPPLD'
        header.update(lastkey,
                      self.appstring,
                      'to which domains was SAA cleaning applied',
                      after='SAACRMAP')


        #Then work forward from the beginning of the section:

        #First put in a comment card as a separator
        header.add_blank('',before=lastkey)
        header.add_blank('      / SAA_CLEAN output keywords',before=lastkey)
        header.add_blank('',before=lastkey)

        #Then describe the persistence image:
        header.update('SAAPERS',
                      os.path.basename(pars.saaperfile),
                      'SAA persistence image',
                      before=lastkey)
        if not pars.readsaaper:
            header.update('SCNPSCL',
                          pars.scale,
                          'scale factor used to construct persistence img',
                          before=lastkey)
            header.update('SCNPMDN',
                          pars.saaper_median,
                          'median used in flatfielding persistence image',
                          before=lastkey)
        header.add_blank('',before=lastkey)

        #Describe the domains
        header.update('SCNTHRSH',
                      self.thresh,
                      'Threshold dividing high & low signal domains',
                      before=lastkey)
        header.update('SCNHNPIX',
                      self.domains['high'].npix,
                      'Number of pixels in high signal domain (HSD)',
                      before=lastkey)
        header.update('SCNLNPIX',
                      self.domains['low'].npix,
                      'Number of pixels in low signal domain (LSD)',
                      before=lastkey)
        header.add_blank('',before=lastkey)

        #Describe the results in each domain
##         self.h.update('SCNGAIN',
##                       self.gainplot,
##                       'gain used for effective noise calculations',
##                       before=lastkey)
        for k in self.domains:
            HorL=k[0].upper()
            header.update('SCN%sCHI2'%HorL,
                          self.domains[k].chi2,
                          '%sSD chi squared for parabola fit'%HorL,
                     before=lastkey)
            header.update('SCN%sSCL'%HorL,
                          self.domains[k].scale,
                          '%sSD scale factor for min noise'%HorL,
                      before=lastkey)
            bestloc=self.domains[k].bestloc
            header.update('SCN%sEFFN'%HorL,
                          self.domains[k].pp[1,bestloc]*self.gainplot,
                          '%sSD effective noise at SCNGAIN'%HorL,
                          before=lastkey)
            header.update('SCN%sNRED'%HorL,
                          self.domains[k].nr,
                          '%sSD  noise reduction (percent)'%HorL,
                          before=lastkey)
##................................................................
## Only needed for testing: removed for release
##................................................................
##             self.h.update('SCNTAG',
##                           tag,
##                           'Tag/description of this version',
##
##................................................................

#..........................................................................
# Exception definitions
class NoPersistError(exceptions.Exception):
    pass
class BadThreshError(exceptions.Exception):
    pass
class NegScaleError(exceptions.Exception):
    pass
class InsuffImprovement(exceptions.Exception):
    pass
class AlreadyDone(exceptions.Exception):
    pass
#.............................................................................
#Helper functions:
#-............................................................................
def osfn(filename):
    """Return a filename with iraf syntax and os environment names substituted out"""
    if filename is None:
        return filename
    return fileutil.osfn(filename)

def writeimage(image, filename, header=None,comment=None,clobber=False):
  hdulist=pyfits.HDUList()
  hdu=pyfits.PrimaryHDU(header=header)
  hdu.data=image
  if (comment is not None):
    hdu.header.add_comment(comment)
  hdulist.append(hdu)
  hdulist.writeto(filename,clobber=clobber)

#..........................................................................
# Math functions
def median(a):
    return N.sort(a.ravel())[a.size / 2]

def parabola_model(coeffs,t):
    r=coeffs[0]*(t-coeffs[1])**2 + coeffs[2]
    return r

def parabola_min(thedata, startguess):
    #We may not need to rescale the data
    guesscoeff=(100,startguess,0.1)
    fitcoeff,chi2,itertrace=LeastSquares.leastSquaresFit(parabola_model,guesscoeff,thedata)
    print "chi2 for parabola fit = ",chi2
    return fitcoeff[1],chi2,itertrace
#............................................................................
#Functions for gauss-poly fitting of the persistence image histogram
def gausspoly_eval(coeffs,t):
    z=(t-coeffs[1])/coeffs[2]
    zz=-1*(z**2/2.)
    r=coeffs[0]*N.exp(zz) + coeffs[3] + coeffs[4]*t + coeffs[5]*t**2
    return r

def gausspoly_model(coeffs,t):
    import math
    z=(t-coeffs[1])/coeffs[2]
    zz=-1*(z**2/2.)
    r=coeffs[0]*zz.exp() + coeffs[3] + coeffs[4]*t + coeffs[5]*t**2
    return r

def gausspoly_fit(thedata,guesscoeff):
    #coeffs are:
    #  amplitude of gaussian: guess max(data)
    #  center of gaussian: guess mode(data)
    #  sigma of gaussian: guess stddev(data)
    #  constant: guess 0.1
    #  linear term: guess 0.1
    #  quadratic term: guess 0.0

    fitcoeff,chi2,itertrace=LeastSquares.leastSquaresFit(gausspoly_model,
                                               guesscoeff,
                                               thedata)
    return fitcoeff, chi2, itertrace

#...........................................................................
def thresh_from_gausspoly_fit(saa, parbinwidth=0.5, nclip=3,
                              diagfile=None, clobber=False):
    """ Some massaging of the SAApersistence image histogram is
    performed in order to obtain an optimal fit.
    Unfortunately this involves some magic numbers taken from
    the IDL code."""
    #Work in a bigger dynamic range space
    im=saa*500.0
    binwidth=parbinwidth*500.0

    #Compute the histogram
    hnbins=int( (10000+100)/binwidth) + 1
    h=histogram1d(im,hnbins,binwidth,-100)
    xloc=N.arange(h.nbins)*h.binWidth+h.minValue

    #Select out only the data range we're interested in
    #Take a first guess at the standard deviation
    idx=((im >= -100) & (im <= 10000))
    yy=imstat(im[idx],binwidth=0.1,nclip=3,fields='stddev')

    #Set up the data we're going to fit
    if hnbins > 600:
        numpoints=600
    else:
        numpoints=hnbins

    thedata = [(xloc[i],h.histogram[i]) for i in range(numpoints)]
    t=xloc[0:numpoints]

    #Now set up the start guesses
    hmax=h.histogram[0:numpoints].max()
    hbinmax=xloc[h.histogram[0:numpoints].argmax()]
    startguess=[hmax,
                xloc[h.histogram[0:numpoints].argmax()],
                yy.stddev,
                0.1, 0.1, 0.0]

    #Do the fitting: with a catch for a linear algebra failure
    try:
        coeffs,chi2,itertrace=gausspoly_fit(thedata,startguess)
    except LinAlgError, e:
        if diagfile is None:
            diagfile='diag_linalgerr'
        f=smartopen(diagfile+'_gp_hist.txt','w',clobber=clobber)
        for k in range(len(t)):
            line = "%f   %d\n"%(t[k],h.histogram[k])
            f.write(line)
        f.close()
        raise e

    #and tell us about the results
    print "\nCoefficients for gauss-poly fit to persistence model histogram:"
    r=itertrace[-1] #Last iteration

    print "Gaussian (low signal component) terms:"
    print "  Amplitude, Mean, Sigma: %f %f %f"%(r[0].value,r[1].value,r[2].value)
    print "Polynomial terms:"
    print "  Constant, Linear, Quadratic:%f %f %f"%(r[3].value,r[4].value,r[5].value)
    print""

    if diagfile:

        #This prints the histogram that is actually fit
        f=smartopen(diagfile+'_gp_hist.txt','w',clobber=clobber)
        for k in range(len(t)):
            line = "%f   %d\n"%(t[k],h.histogram[k])
            f.write(line)
        f.close()

        #and this prints the series of coefficients for each iteration
        f=smartopen(diagfile+'_gp_iters.txt','w',clobber=clobber)
        for p in (itertrace):
            line='   '.join([str(x[0]) for x in p])+"\n"
            f.write(line)
        f.close()

##     for k in range(len(itertrace)):
##         print "Iter %d"%k,itertrace[k]

    #Finally, compute the threshold based on the fit.
    #Don't forget to divide out the magic-number to convert back
    #to the original scale.

    thresh=(coeffs[1] + 3.5*abs(coeffs[2]))/500.
    return thresh

#..............................................................................
# General functions
#..........................................................................
def get_postsaa_darks(imgfile):
    """ Return the filenames containing the post-saa dark exposures, if
    present. Otherwise raise an exception and exit. """

    #Get the science header
    inpath=os.path.dirname(osfn(imgfile))
    if inpath != '':
        inpath+= '/'
    f=pyfits.open(imgfile)
    h=f[0].header
    saa_asn=h['saa_dark']
    f.close()
    if saa_asn == 'N/A':
        raise NoPersistError, """This data was not taken in an SAA-impacted orbit.
        No correction needed. Exiting."""
    else:
        #Get the files out of that set
        saa_files=[]
        f2=pyfits.open(inpath+saa_asn.lower()+'_asn.fits')
        for i in [0,1]:
            name=f2[1].data[i]
            saa_files.append(inpath+name.field(0).lower()+'_raw.fits')
        f2.close()
        return saa_files

def getdark(camera,tdkfile,darkpath):
    """ Get the right dark file for a given NICMOS camera.
    This is definitely not the right way to do this."""
    dfile={1:'c1_saadarkref_drk.fits',
           2:'c2_saadarkref_drk.fits',
           3:'c3_saadarkref_drk.fits'}
    darkpath=os.path.abspath(darkpath)+'/'
    defaultfile=darkpath+dfile[camera]
    #Choose which file to use
    if tdkfile:
        altfile=darkpath+os.path.basename(tdkfile)
        if os.path.isfile(tdkfile):
            thefile=tdkfile
        elif os.path.isfile(altfile):
            thefile=altfile
        else:
            thefile=defaultfile
    else:
        thefile=defaultfile
    #Return the data from it
    f=pyfits.open(thefile)
    ans= f[1].data
    f.close()
    return ans

def make_saaper(imgfile,pars,crthresh=1):
    # Get dark data here
    im1,im2,dark=get_dark_data(imgfile,pars.darkpath)

    #Process the data
    for im in [im1,im2]:
        im.dark_subtract(dark)
        im.pedskyish()
    #Combine the data
    saaper=((im1.data*pars.wf1) + (im2.data/pars.scale)*pars.wf2)
    #Correct for CRs
    if pars.crthresh:
        a=im1.data-(im2.data/pars.scale)
        u1=N.where(a > pars.crthresh)
        saaper[u1]=im2.data[u1]/pars.scale

        a=(im2.data/pars.scale) - im1.data
        u2=N.where(a > pars.crthresh)
        saaper[u2]=im1.data[u2]
    if pars.writesaaper and pars.saaperfile:
        hdr = create_saaper_header(im1,im2,saaper)
        hdr['filename'] = pars.saaperfile # update filename for new output
        writeimage(saaper,pars.saaperfile,clobber=pars.clobber,header=hdr)
    return saaper


def get_dark_data(imgfile,darkpath):
    saafiles=get_postsaa_darks(imgfile)
    im1=Exposure(saafiles[0],nickname='postsaa dark #1')
    im2=Exposure(saafiles[1],nickname='postsaa dark #2')
    dark=getdark(im1.camera,im1.tdkfile,darkpath)
    return im1,im2,dark

def create_saaper_header(im1,im2,saaper):
    # User the header from the first SAA image as the template
    hdr = pyfits.Header()
    # Update keywords to make final combined header
    # By default, use the value from 'im1'
    pkeys = ['filename','targname','imagetyp','date-obs','time-obs',
            'exptime','expstart','expend', 'saa_exit','saa_time',
             'adcgain','camera','saadfile','maskfile']

    # Build up header from list of keywords
    for k in pkeys:
        # Find out index of card with this keyword from im1 header
        kindx = im1.h.index(k)
        # copy entire card from im1 header to new header for this keyword
        # this preserves the comment as well as the value
        hdr.append(im1.h.cards[kindx])

    #Now for those keywords which need special attention...
    hdr['imagetyp'] = 'SAAPER'
    hdr['expend'] = im2.h['expend']
    hdr['exptime'] = im1.h['exptime'] + im2.h['exptime']
    hdr['bunit'] = 'COUNTS'  # based on input value from im1
    hdr['datamin'] = saaper.min()
    hdr['datamax'] = saaper.max()
    hdr['date'] = (fileutil.getDate(), 'Date this file was written')

    return hdr

def flat_saaper(saaper,img):
    #The "midpt" computes a pseudo-median function.
    mm=imstat(saaper,nclip=1,binwidth=0.01,fields='midpt').midpt
    #Use median, or mode? which is better?
    if img.h['flatdone'] == 'PERFORMED':
        flatname=osfn(img.h['flatfile'])
##         if flatname.startswith('nref$'):
##             prefix,root=flatname.split('$',1)
##             flatname=iraf.osfn(prefix+'$')+root
        flat=Exposure(flatname,nickname='flatfile')

        print "median used in flatfielding: ",mm
        saaper=((saaper-mm)*flat.data) + mm
    return saaper,mm


def smartopen(fname, mode, clobber=True):
    """ Allows specifying a clobber behavior """
    if mode.startswith('w') and not clobber:
        if os.path.isfile(fname):
            raise IOError, "%s already exists"%fname

    handle=open(fname,mode)
    return handle

#....................................................................
# The "main" program
#....................................................................
def clean(usr_calcfile,usr_targfile,usr_outfile,pars=None):
    numerixenv.check() #Temporary NUMERIX environment check
    print "Input files: %s %s"%(usr_calcfile,usr_targfile)
    imgfile=osfn(usr_calcfile)
    img=Exposure(imgfile,nickname='sci image')
    targfile=osfn(usr_targfile)
    if imgfile != targfile:
        #then we'll need the data from the targfile
        targ=Exposure(targfile,nickname='target image')
        appimage=targ.data.copy()
    else:
        #we'll apply it to the same file
        targ=img
        appimage=None


    #Check to make sure we're not trying to run the task twice
    #on the same image
    already_done=['low everywhere','both','high only']
    for check in [targ,img]:
        scnappld=check.h.get('scnappld',None)
        if scnappld in already_done:
            raise AlreadyDone, check.filename

    outfile=osfn(usr_outfile)
    if pars is None:
        pars=params()
    if pars.readsaaper:
        sfile=pyfits.open(pars.saaperfile)
        saaper=sfile[0].data
        sfile.close()
    else:
        saaper=make_saaper(imgfile,pars)
        print "Using scale factor of ",pars.scale," to construct persistence image"


    mask,badmask=img.getmask(writename=pars.maskfile,clobber=pars.clobber)
    saaper,mm=flat_saaper(saaper,img)
    pars.saaper_median=mm

    if pars.flatsaaperfile:
        writeimage(saaper,pars.flatsaaperfile,clobber=pars.clobber)

    mask,badmask=img.getmask(writename=None)
    img.apply_mask(mask)

    if pars.fitthresh:
        img.thresh  = thresh_from_gausspoly_fit(saaper,
                                                parbinwidth=pars.histbinwidth,
                                                nclip=pars.nclip,
                                                diagfile=pars.diagfile,
                                                clobber=pars.clobber)
    else:
        img.thresh=pars.thresh


    print "Threshold for hi/lo: ",img.thresh

    #Apply threshold *to persistence image*
    img.domains={'high':Domain('high',
                               N.where(saaper > img.thresh),
                               pars.hirange),
                 'low' :Domain('low',
                               N.where(saaper <= img.thresh),
                               pars.lorange)
                 }


    print "Npixels hi/lo: ",len(img.domains['high'].pixlist[0]),len(img.domains['low'].pixlist[0])

    #Do some checking for sensible results
##     if (img.domains['high'].npix == 0):
##         raise BadThreshError,"ERROR: Zero pixels found in high signal domain."
    if (img.domains['high'].npix > img.domains['low'].npix):
        raise BadThreshError,"ERROR: Number of high domain pixels exceeds the number of low domain pixels"
    img.getscales(saaper,mask,pars)

    final=img.apply_domains(saaper,badmask,pars.noisethresh,appimage=appimage)


    if 1: #img.update:
        targ.data=final
        img.update_header(pars,header=targ.h)
        targ.writeto(outfile,clobber=pars.clobber)


    return saaper,img
