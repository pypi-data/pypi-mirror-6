import os
import sys
try:
    from astropy.io import fits
except:
    import pyfits as fits

import cpl

class ProcessingInfo(object):
    '''This class contains support for reading input files and parameters from
    the FITS header of a CPL processed file.

    This is done through the FITS headers that were written by the DFS function
    called within the processing recipe.

    .. attribute:: name 

       Recipe name

    .. attribute:: version 

       Recipe version string

    .. attribute::  pipeline

       Pipeline name

    .. attribute:: cpl_version
    
       CPL version string

    .. attribute:: tag

       Tag name

    .. attribute:: calib

       Calibration frames from a FITS file processed with CPL.
       The result of this function may directly set as :attr:`cpl.Recipe.calib`
       attribute::
    
         import cpl
         myrecipe = cpl.Recipe('muse_bias')
         myrecipe.calib = cpl.dfs.ProcessingInfo('MASTER_BIAS_0.fits').calib

       .. note::

          This will not work properly for files that had
          :class:`astropy.io.fits.HDUList` inputs since they have assigned a
          temporary file name only.

    .. attribute:: raw

       Raw (input) frames

       .. note::

          This will not work properly for files that had
          :class:`astropy.io.fits.HDUList` inputs since they have assigned a
          temporary file name only.

    .. attribute:: param

       Processing parameters.
       The result of this function may directly set as :attr:`cpl.Recipe.param`
       attribute::
    
         import cpl
         myrecipe = cpl.Recipe('muse_bias')
         myrecipe.param = cpl.dfs.ProcessingInfo('MASTER_BIAS_0.fits').param

    .. attribute:: md5sum

       MD5 sum of the data portions of the output file (header keyword 
       'DATAMD5').

    .. attribute:: md5sums

       MD5 sums of the input and calibration files. :class:`dict` with the
       file name as key and the corresponding MD5 sum as value.

       .. note::

          Due to a design decision in CPL, the raw input files are not
          accompanied with the MD5 sum.
    '''

    def __init__(self, source, datapaths = None):
        '''
        :param source: Object pointing to the result file header
        :type source: :class:`str` or :class:`astropy.io.fits.HDUList`
                      or :class:`astropy.io.fits.PrimaryHDU` or 
                      :class:`astropy.io.fits.Header`
        :param datapaths: Dictionary with frame tags as keys and directory paths
                        as values to provide a full path for the raw and
                        calibration frames. Optional.
        :type datapaths: :class:`dict`
        '''
        if isinstance(source, str):
            header = fits.open(source)[0].header
        elif isinstance(source, fits.HDUList):
            header = source[0].header
        elif isinstance(source, fits.PrimaryHDU):
            header = source.header
        elif isinstance(source, (fits.Header, dict)):
            header = source
        else:
            raise ValueError('Cannot assign type %s to header' % 
                             source.__class__.__name__)
        
        self.name = header['HIERARCH ESO PRO REC1 ID']
        self.product = header['HIERARCH ESO PRO CATG']
        self.orig_filename = header['PIPEFILE']
        if datapaths and self.product in datapaths:
            self.orig_filename = os.path.join(datapaths[self.product], 
                                              self.orig_filename)
        pipe_id = header.get('HIERARCH ESO PRO REC1 PIPE ID')
        if pipe_id:
            self.pipeline, version = pipe_id.split('/')
            num_version = 0
            for i in version.split('.'):
                num_version = num_version * 100 + int(i)
            self.version = (num_version, version)
        else:
            self.pipeline =  None
            self.version = None
        self.cpl_version = header.get('HIERARCH ESO PRO REC1 DRS ID')
        self.md5sum = header.get('DATAMD5')
        self.md5sums = {}
        self.calib = _get_rec_keys(header, 'CAL', 'CATG', 'NAME', datapaths)
        for cat, md5 in _get_rec_keys(header, 'CAL', 'CATG', 'DATAMD5').items():
            if isinstance(md5, list):
                for m, f in zip(md5, self.calib[cat]):
                    if m is not None: 
                        self.md5sums[f] = m
            elif md5 is not None:
                self.md5sums[self.calib[cat]] = md5
        raw = _get_rec_keys(header, 'RAW', 'CATG', 'NAME', datapaths)
        if raw:
            self.tag = list(raw.keys())[0]
            self.raw = raw[self.tag]
            md5 = _get_rec_keys(header, 'RAW', 'CATG', 'DATAMD5')[self.tag]
            if isinstance(md5, list):
                for m, f in zip(md5, self.raw):
                    if m is not None: 
                        self.md5sums[f] = m
            elif md5 is not None:
                self.md5sums[self.raw] = md5
        else:
            self.tag = None
            self.input = None
        param = _get_rec_keys(header, 'PARAM', 'NAME', 'VALUE')
        self.param = dict()
        for k,v in param.items():
            self.param[k] = _best_type(v)
            
    def create_recipe(self):
        recipe = cpl.Recipe(self.name)
        recipe.param = self.param
        recipe.calib = self.calib
        recipe.tag = self.tag
        return recipe

    def create_script(self, scriptfile = sys.stdout):
        if isinstance(scriptfile, str):
            scriptfile = file(scriptfile, mode='w')
        scriptfile.write('import cpl\n\n')
        scriptfile.write('# Recipe: %s.%s, Version %s, CPL version %s\n' % 
                         (self.pipeline, self.name, self.version[1], 
                          self.cpl_version))
        scriptfile.write('%s = cpl.Recipe(%s, version = %s)\n' % 
                         (self.name, repr(self.name), repr(self.version[0])))
        scriptfile.write('\n# Parameters:\n')
        for k,v in self.param.items():
            scriptfile.write('%s.param.%s = %s\n' % (self.name, k, repr(v)))
        if self.calib:
            scriptfile.write('\n# Calibration frames:\n')
        for k,v in self.calib.items():
            scriptfile.write('%s.calib.%s = %s\n' % (self.name, k, repr(v)))
        scriptfile.write('\n# Process input frames:\n')
        scriptfile.write('%s.tag = %s\n' % (self.name, repr(self.tag)))
        scriptfile.write('res = %s(%s)\n' % (self.name, repr(self.raw)))
        scriptfile.write('%s = res.%s\n' % (self.product.lower(), self.product))
        scriptfile.write('%s.writeto(%s)\n' % (self.product.lower(), 
                                               repr(self.orig_filename)))

    def printinfo(self):
        print('Recipe: %s, Version %s, CPL version %s ' % (
                self.name, self.version, self.cpl_version))
        print('Parameters:')
        for k,v in self.param.items():
            print(' %s.%s.%s = %s' % (self.pipeline, self.name, k, v))
        if self.calib:
            print('Calibration frames:')
        for k,v in self.calib.items():
            if isinstance(v, str):
                print(' %s %s' % (v,k))
            else:
                for n in v:
                    print(' %s %s' % (n,k))
        print('Input frames:')
        if isinstance(self.raw, str):
            print(' %s %s' % (self.raw, self.tag))
        else:
            for n in self.raw:
                print(' %s %s' % (n, self.tag))

def _get_rec_keys(header, key, name, value, datapaths = None):
    '''Get a dictionary of key/value pairs from the DFS section of the
    header.

    :param key: Common keyword for the value. Usually 'PARAM' for 
                parameters, 'RAW' for raw frames, and 'CAL' for 
                calibration frames.
    :type key: :class:`str`
    :param name: Header keyword (last part) for the name of each key
    :type name: :class:`str`
    :param value: Header keyword (last part) for the value of each key
    :type name: :class:`str`
    :param datapaths: Dictionary with frame tags as keys and directory paths 
                    as values to provide a full path for the raw and 
                    calibration frames. Optional.
    :type datapaths: :class:`dict`

    When the header
    
      HIERARCH ESO PRO REC1 PARAM1 NAME = 'nifu'
      HIERARCH ESO PRO REC1 PARAM1 VALUE = '1'
      HIERARCH ESO PRO REC1 PARAM2 NAME = 'combine'
      HIERARCH ESO PRO REC1 PARAM2 VALUE = 'median'
      
    is called with

      _get_rec_keys('PARAM', 'NAME', 'VALUE')

    the returned dictionary will contain the keys

      res['nifu'] = '1'
      res['combine'] = 'median'
    '''
    res = dict()
    for i in range(1, 2**16):
        try:
            prefix = 'HIERARCH ESO PRO REC1 %s%i' % (key, i)
            k = header['%s %s' % (prefix, name)]
            fn = header.get('%s %s' % (prefix, value))
            if datapaths and k in datapaths:
                fn = os.path.join(datapaths[k], fn)
            if k not in  res:
                res[k] = fn
            elif isinstance(res[k], list):
                res[k].append(fn)
            else:
                res[k] = [ res[k], fn ]
        except KeyError:
            break
    return res
    
def _best_type(value):
    '''Convert the value to the best applicable type: :class:`int`, 
    :class:`float`, :class:`bool` or :class`str`.

    :param value: Value to convert.
    :type value: :class:`str`
    '''
    for t in int, float:
        try:
            return t(value)
        except ValueError:
            pass
    return {'true':True, 'false':False}.get(value, value)

if __name__ == '__main__':
    import sys

    datapaths = {
        'BIAS':'raw', 'DARK':'raw', 'FLAT':'raw', 'ARC':'raw', 'OBJECT':'raw', 
        'LINE_CATALOG':'aux', 'TRACE_TABLE':'aux', 'GEOMETRY_TABLE':'aux',
        'MASTER_BIAS':'result', 'MASTER_DARK':'result', 'MASTER_FLAT':'result',
        'WAVECAL_TABLE':'result', 'PIXTABLE_OBJECT':'result', 
        }
    for arg in sys.argv[1:]:
        print('---------------------')
        print('file: %s' % arg)
        pi = ProcessingInfo(arg, datapaths = datapaths)
        pi.printinfo()
