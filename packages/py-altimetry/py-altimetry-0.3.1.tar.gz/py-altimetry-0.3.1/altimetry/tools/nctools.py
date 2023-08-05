# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab

#from grid.regridding import griddata, xy2xy

from netCDF4 import Dataset as ncfile
import glob
import os
from altimetry.tools import recale, in_limits, where_list, recale_limits, get_caller, isiterable
#import altimetry.data.alti_tools as atools
from collections import OrderedDict
from warnings import warn
from copy import deepcopy

class baseDict(OrderedDict):
    
    def __init__(self, *args, **kwargs):
        keys=kwargs.pop('keys',None)
        values=kwargs.pop('values',None)
         
        if len(args) == 0 : args =(self,)
        
        #If 2 arguments, both list arguments become keys and args 
        elif len(args) == 2 :
            if (isinstance(args[0],list) or isinstance(args[0],tuple)) and (isinstance(args[1],list) or isinstance(args[1],tuple)) and (keys is None) and (values is None) :
                keys,values=args
                args = (self,)
        #else len(args) == 1 : an object instance is passed
        
        super(baseDict,self).__init__(*args,**kwargs)
        
        if keys is not None and values is not None :
            self.add(keys,values)
        
    def copy(self):   
        return deepcopy(self)

class dimStr(baseDict):
    '''
    A dimension structure based on OrderedDict.
    '''
    
    def __init__(self,*args,**kwargs):
        super(dimStr, self).__init__(*args, **kwargs)
        self.set_ndims(__init__=True)
        
    def get_ndims(self):
        return len([k for k in self.keys() if k is not '_ndims'])
    
    def set_ndims(self,__init__=False,__setitem__=False):
        #Modify _ndims if it exists or during __init__
        if self.has_key('_ndims') or __init__ :
            
            self['_ndims']=self.get_ndims()
            
            #Force pushing _ndims in first
            if (not __setitem__) : self.reorder()
            
    
    def reorder(self):
        if self.has_key('_ndims') :
            if self['_ndims'] > 0 :
                for k in self.keys():
                    self[k]=self.pop(k)
                pass
            
    
    #===========================================================================
    # Work with dimensions
    #===========================================================================
    def add(self,dimlist,dimvalues):
        '''
        add dimensions
        
        :parameter dimlist: list of dimensions
        :parameter dimvalues: list of values for dimlist
        '''
        for i,d in enumerate(dimlist):
            self[d] = dimvalues[i]
        
        self.set_ndims()
    
    def put(self,*args):
        '''
        Wrapper to add
        '''
        self.addDim(*args)
        
        
    def get(self,dimlist):
        '''
        get dimensions
        :parameter dimlist: list of dimensions
        '''
        out=()
        for i,d in enumerate(dimlist):
            out+=(super(dimStr, self).get(d,None),)
         
        return out
    
    def pop(self,*args):
        '''
        pop dimensions
        :parameter dimlist: list of dimensions
        :return: popped dimensions (tuple)
        
        .. note: overrides :func:`OrderedDict.pop`
        '''
        nargs=len(args)
        dimlist=args[0] if isiterable(args[0]) else [args[0]]
        missing=args[1] if nargs > 1 else None 
        out=()
        for d in dimlist:
            out+=(super(dimStr, self).pop(d,missing),)
            if out[-1] == missing : self.set_ndims()
        
        return out if len(out) > 1 else out[0]

    def __setitem__(self, *args,**kwargs):
        OrderedDict.__setitem__(self, *args, **kwargs)
        if args[0] != '_ndims' :self.set_ndims(__setitem__=True)

    def keys(self):
        return [k for k in super(dimStr, self).keys() if k != '_ndims']

    def values(self):
        return [self[k] for k in super(dimStr, self).keys() if k != '_ndims']

class attrStr(baseDict):
    '''
    An attribute structure based on OrderedDict.
    '''
    
#     def __init__(self,*):
#         super(attrStr,self).__init__()
#         if attrlist is not None : self.add(attrlist,attrlist)
    
    def add(self,attrlist,attrvalues):
        '''
        add an attribute
        
        :parameter dimlist: list of dimensions
        :parameter dimvalues: list of values for dimlist
        '''
        for i,d in enumerate(attrlist):
            self[d] = attrvalues[i]
    
    def put(self,*args):
        '''
        Wrapper to addDim
        '''
        self.addDim(*args)
        
        
#     def get(self,dimlist):
#         '''
#         '''
#         out=()
#         for d in enumerate(dimlist):
#             out+=(self['_dimensions'].get(d,None),)
#         
#         return out
    
    def pop(self,*args):
        '''
        pop dimensions from data structure.
        :parameter dimlist: list of dimensions
        :return: popped dimensions (tuple)
        
        .. note: overrides :func:`OrderedDict.pop`
        '''
        nargs=len(args)
        dimlist=args[0] if isiterable(args[0]) else [args[0]]
        missing=args[1] if nargs > 1 else None 
        out=()
        for d in dimlist:
            out+=(super(attrStr, self).pop(d,missing),)
        
        return out if len(out) > 1 else out[0]
    
class dataStr(baseDict):
    '''
    Data structure class to be used with altimetry.tools.nctools.nc
    '''
    
    def __init__(self,*args,**kwargs):
        super(dataStr,self).__init__(*args,**kwargs)
        self['_dimensions']=dimStr()
        '''
        Dimensions structure
        '''
        
        self['_attributes']=attrStr()
        '''
        Attributes structure
        '''
    
    def add(self,struct):
        if isinstance(struct,varStr): self[struct.getVarName(self)]=struct
        elif isinstance(struct,attrStr): self['_attributes'].put(struct)
        elif isinstance(struct,dimStr): self['_dimensions'].put(struct)
    
    def put(self,*args):
        self.add(*args)
    
    def getStructVars(self):
        return [k for k in self.keys() if isinstance(self[k],varStr)]
    
    def getStructDims(self):
        return [k for k in self.keys() if isinstance(self[k],dimStr)]
    
    def getStructAttr(self):
        return [k for k in self.keys() if isinstance(self[k],attrStr)]
    
class varStr(dataStr):
    '''
    Data structure class containing variables
    
    :keyword name: Name of the variable. Stored in :attr:`varStr.name`
    :keyword (dimStr,dict or OrderedDict) dimensions: Dimension structure .
    :keyword dimlist: list of variable dimension names. Their order will be kept.
    :keyword optional dimvalues: list of values associated with dimlist.
        
    :keyword (attrStr,dict or OrderedDict) attributes: Attribute structure.
    :keyword attrlist: list of variable attribute names. Their order will be kept.
    :keyword optional attrvalues: list of values associated with attrist.
    
    
    .. note : if dict are used in :param:`dimensions` and :param:`attributes`, dimensions may not be in proper order. Use dimlist and attrlist instead to keep order.
      
    '''
    
    def __init__(self,
                 name=None,
                 dimensions=None,
                 dimlist=None,
                 dimvalue=None,
                 attributes=None,
                 attrlist=None,
                 attrvalues=None,
                 data=None):
        
        #Init parent object
        dataStr.__init__(self)
        
        #Set variable name
        self.name = name
        
        #Set variable dimensions
        if dimensions is not None and isinstance(dimensions,(dimStr,dict,OrderedDict)):
            dimlist = dimensions.keys()
            dimvalue = dimensions.values()
        if dimlist is not None :
            if dimvalue is None : dimvalue = [None for d in dimlist]
            self['_dimensions'].add(dimlist,dimvalue)
        
        #Set variable attributes
        if attributes is not None and isinstance(attributes,(attrStr,dict,OrderedDict)):
            attrlist = attributes.keys()
            attrvalues = attributes.values()
        if attrlist is not None :
            self['_attributes'].add(attrlist,attrvalues)
        
        #Set variable data
        if data is not None : self['data']=data
        
        #Reform attributes
        for d in self['_attributes'].keys():
            self[d] = self['_attributes'].pop(d)
        self.pop('_attributes')
        
    def getVarName(self,parent):
        
        name = None
        if hasattr(self, 'name') : name =  self.__dict__.pop('name',None)
        
        if name is None :
            varNames=parent.getStructVars()
            if len(np.shape(self['data'])) == 1 :
                nvars = len([v for v in varNames if v.startswith("Param_")])
                name =  "Param_%04i" % (nvars+1)
            elif len(np.shape(self['data'])) == 2 :
                nvars = len([v for v in varNames if v.startswith("Grid_")])
                name = "Grid_%04i" % (nvars+1)
            elif len(np.shape(self['data'])) == 3 :
                nvars = len([v for v in varNames if v.startswith("Matrix_")])
                name = "Matrix_%04i" % (nvars+1)
        
        return name

class ncStr(dataStr):
    '''
    Data structure class containing NetCDF data.
    '''
    
    def __init__(self,
                 dimlist=None,
                 dimvalues=None,
                 attrlist=None,
                 attrvalues=None):
        
        dataStr.__init__(self)
        if dimlist is not None : self['_dimensions'].add(dimlist,dimvalues)
        if attrlist is not None : self['_attributes'].add(attrlist,attrvalues)
    

class nc :
    
    '''
    A class for easy-handling of NetCDF data based on :mod:`NetCDF4` package.
    
    :example: To load different sets of data, try these :
    
      * Simply load a NetCDF file
         
        * The file has standard dimensions (eg. called longitude & latitude)
        
        .. code-block:: python
         
           ncr=nc()
           data=ncr.read(file)
         
           lon=data.lon
           lat=data.lat
           Z=data.Z
        
        * We do not want to match for standard dimension names and keep original names
        
        .. code-block:: python
           :emphasize-lines: 2,4-5
         
           ncr=nc()
           data=ncr.read(file,use_local_dims=True)
           
           lon=data.longitude
           lat=data.latitude
           Z=data.Z
        
         
        * We extract a region and depth range between 2 dates:
        
          * We extract between 30-40°N & 15-20°E (limit).
          * We extract between 100 & 200 m deep (depth).
          * We get data from 2010/01/01 to 2010/01/07 (time).
          * File has standard dimensions called longitude, latitude, level and time
        
        .. code-block:: python
           :emphasize-lines: 7-9
         
           ncr=nc()
           limit=[30,15,40,20]
           depth=[100,200]
           time=[21915,21921]
           
           data=ncr.read(file,
                         limit=limit,
                         timerange=time,
                         depthrange=depth)
             
           lon=data.lon
           lat=data.lat
           dep=data.depth
           dat=data.time
           Z=data.Z
    
    
      * More sophisticated example using a file containing bathymetetry data
        
        * Load a file and extract a regions and subsample it to a lower resolution
         
          * The file has dimensions NbLongitudes & NbLatitudes.
          * We extract between 30-40°N & 15-20°E (limit).
          * We subsample every 3 points (stride).
       
        .. code-block:: python
           :emphasize-lines: 5-6
        
           limit=[30,15,40,20]
           stride = (3,)
           ncr=nc(use_local_dims=True)
           bathy=ncr.load(file,
                          NbLongitudes=(limit[1],limit[3])+stride,
                          NbLatitudes=(limit[0],limit[2])+stride)
       
        
        * Then we save the data to another file (output).
       
        .. code-block:: python
          
           #save data
           bathy.write_nc(output)
        
        * We update the **history** global attribute of data structure
       
        .. code-block:: python
           :emphasize-lines: 9,12
          
           #Get attribute structure
           attrStr=bathy.get('_attributes',{})
            
           #Get arguments called from the shell
           cmd=[os.path.basename(sys.argv[0])]
           for a in argv : cmd.append(a)
            
           #update attribute stucture (pop history and concatenate with current commands=.
           attrStr.update({'history':attrStr.pop('history','')+' '.join(cmd)+'\\n'})
            
           #update NetCDF data structure
           bathy.update({'_attributes':attrStr})
          
           #save data
           bathy.write_nc(output)
        
        
        * We now want to flag all values from variable Z above 0 by setting them to fill_value and append this modified variable to the output file
      
        .. code-block:: python
          
           #load variable
           Z = bathy.Z
         
           #flag variable
           Z.mask[Z >= 0] = False
         
           #update attributes
           Z['_attributes']['long_name'] = 'flagged bathymetry'
         
           #append modified bathymetry to a variable named Z_2 in output file.
           bathy.push(output,'Z2',Z)
           
    '''
    
    def __init__(self, limit=[-90., 0., 90., 360.], verbose=0, zero_2pi=False, transpose=False, use_local_dims=False, **kwargs):
        '''
        Returns an :class:`altimetry.tools.nctools.nc` instance.
        
        :keyword limit: the limits of the domain to handle ([latmin,lonmin,latmax,lonmax]).
        :keyword verbose: verbosity level on a scale of 0 (silent) to 4 (max verobsity)
        :keyword zero_2pi: limits goes from 0 to 360 degrees (not -180/180).
        :keyword use_local_dims: use file dimensions instead of trying to detect standard dimension names (cf. :attr:`altimetry.tools.nctools.nc.use_local_dims`)
        
        '''
        
        #Init system variables
        self.zero_2pi = zero_2pi
        
        self.limit = np.array(recale_limits(limit, zero_2pi=self.zero_2pi))
        '''
        limits of the domain : [latmin,lonmin,latmax,lonmax] (default = [-90.,0.,90.,360.])
        
        .. note:: limits are automatically reset using :func:`altimetry.tools.recale_limits`
        '''
        
        self.verbose = verbose
        '''
        verbosity level on a scale of 0 (silent) to 4 (max verbosity)
        '''
        
        self.fileid = np.array([])
        '''
        array of file IDs
        '''
        
        self.count = 0
        '''
        number of files loaded
        '''
        
        self.size = 0
        '''
        length of the dataset
        '''

        self.use_local_dims=use_local_dims
        '''
        this option prevent from trying to detect standard CF dimensions such longitude, latitude, time in the file and keep the original dimensions of the file
        
        .. note:: Set this option to True when file is not standard (eg. not following CF conventions).
        
        .. note:: Normal behaviour is to match dimensions (ie. a dimension and the associated variable of the same name) with specific names. Resulting variables associated with these dimensions will be called :
          * lon (longitudes) : matches dimensions starting with 'lon'
          * lat (latitudes) : matches dimensions starting with 'lat'
          * time (time) : matches dimensions starting with 'date' or 'time'
          * depth (date) : matches dimensions starting with 'dep' or 'lev'
          
        '''
    
    def push(self,*args,**kwargs):#file,varName,value,**kwargs):
        '''
        append a variable from a given data structure to the existing dataset.
        
        :parameter optional file:
        :parameter name: variable name
        :parameter value: data
        
        :keyword start: broadcast the data to a portion of the dataset. starting index.
        :keyword counts: broadcast the data to a portion of the dataset. number of counts.
        :keyword stride: broadcast the data to a portion of the dataset. stepping along dimension.
        
        '''
        
        reload = False
        
        #Get arguments
        largs=list(args)
        if os.path.exists(largs[0]) :
            file = largs.pop(0)
            self._filename = file
            reload = True
        name = largs.pop(0)
        value = largs.pop(0)
        
        #Get keywords
        start = kwargs.get('start',None)
        counts = kwargs.get('counts',None)
        stride = kwargs.get('stride',None)
        
        
        file = self._filename
        
        if self.verbose == 1 : self.message(1, 'Writing data into file {0}'.format(os.path.basename(file)))
        elif self.verbose > 1 : self.message(2, 'Writing data into file {0}'.format(file))
        ncf=ncfile(file, 'a', format='NETCDF4', clobber=False)
     
        #Get list of recorded parameters:
        par_list = ncf.variables.keys()
        
        #Check if variable exists
        if 'sla' not in par_list : createVariable = True
        else : createVariable = False
        
        
        if not createVariable :
            var=ncf.variables[name]
            
            #Get dimensions
            fileDims=OrderedDict({'_ndims':len(var.dimensions)})
            [fileDims.update({str(d):len(ncf.dimensions[d])}) for d in var.dimensions]
            
            if start is None : start = [0 for sh in var.shape]
            else : start = start[::-1]
            if counts is None : counts = [sh for sh in var.shape]
            else : counts = counts[::-1]
            if stride is None : stride = [1 for sh in var.shape]
            else : stride = stride[::-1]
            
            #Transpose before write
            value=np.transpose(value)
            strides=var[:].strides
            
            #Construct indices (cf.http://docs.scipy.org/doc/numpy-1.5.x/reference/arrays.indexing.html)
            ind=()
            for i in np.arange(len(start)) : ind+=(slice(start[i],start[i]+counts[i],strides[i]),)
            
            #Push data into file
            try : var[ind]=value[:]
            except ValueError : self.Error('Input variable {0} {1} cannot be broadcasted into {2}'.format(name,value.shape,os.path.basename(file)))
            
            #Check if variable is in agreement with dimensions
#            dimStr=self._dimensions #Get dimensions  
            
            ncf.close()
            
            
        else :
            self.Error('This option is not yet implemented')
        
        
        
    
    def write(self, data, outfile, clobber=False,format='NETCDF4'):
        '''
        Write a netCDF file using a data structure.
        
        :parameter data: data structure
        :parameter outfile: output file
        :keyword clobber: erase file if it already exists
        :keyword format: NetCDF file format.
        
        .. note :: the data structure requires a "_dimensions" field (dimension structure)
        '''
        
        #Open file
        if self.verbose == 1 : self.message(1, 'Writing data file {}'.format(os.path.basename(outfile)))
        elif self.verbose > 1 : self.message(2, 'Writing data file {}'.format(outfile))
        root_grp=ncfile(outfile, 'w', format=format, clobber=clobber)
#        root_grp.description = 'nctools.write() file'
        
        #Get attributes
        if data.has_key('_attributes'):
            self.message(2, 'Adding attributes data')
            attrStr=data.pop('_attributes')
            self.message(4, 'Attribute list (N={0}) :[{1}]'.format(len(attrStr.keys()), ','.join(attrStr.keys())) )
            root_grp.setncatts(attrStr)
        
        #Get dimensions
        dimDict=data.pop('_dimensions')
        ndims=dimDict.pop('_ndims')
        dimlist = dimDict.keys()
        dimVal = dimDict.values()
        
        #Get variables
        parlist = data.keys()
        
        
        # Set up dimensions
        
        #Put dimensions
        for d in dimlist :
            self.message(2, 'Adding D {0}={1}'.format(d,dimDict[d]))
            root_grp.createDimension(d, dimDict[d])
        
#        if data.has_key('p')  : self.Error('Variable name \'p\' is not available for use as NetCDF variable name')
        
        #Loop over variables
        for p in parlist :
            
            self.message(4,'Looping parameter list : %s' %p)
            
            #Get dimensions for current variable
            if not data[p].has_key('_dimensions') : self.Error('_dimension attribute is not set for variable'+p)
            pardim=data[p].pop('_dimensions')
            if isinstance(pardim,dimStr) : pardim=tuple(pardim.keys())
            elif isinstance(pardim,dict) :pardim=tuple(pardim.keys()[1:]) if pardim.has_key("_ndims") else tuple(pardim.keys())
            elif isinstance(pardim,list) : pardim = tuple(pardim)
            elif isinstance(pardim,tuple) : pass
            else : self.Error('_dimensions must be dict, list or tuple - not {0}'.type(pardim)) 
            
            #Convert to numpy array if scalar or non numpy
            if not hasattr(data[p]['data'],'__iter__') or not hasattr(data[p]['data'], 'dtype'):  data[p]['data']=np.array(data[p]['data'])

            #Get _FillValue if possible
#            if hasattr(data[p]['data'],'fill_value') : data[p]['_FillValue']=data[p]['data'].fill_value 

#            if not (data[p]['data'].dtype == '|S6') and not (data[p]['data'].dtype == '|S2') :
            self.message(2, 'Adding V {0} (dims={{{1}}},attr={{{2}}})'.
                         format(p,
                                ', '.join(['\'{0}\':{1}'.format(d,dimDict[d]) for d in pardim]),
                                ', '.join(['\'{0}\':{1}'.format(d,data[p][d]) for d in data[p].keys() if (d != '_dimensions') and (d != 'data')]) )
                         )
            
            if locals().has_key(p) : self.Error('Variable name \'{0}\' is already declared - change variable name'.format(p))
            
            #Scale it back
            ##############
            
            #look at scaler factors and offsets in both attributes and data structure keys
            scale_factor=scale_factor=data[p].get('scale_factor',None)
            if scale_factor is None : scale_factor=data[p].get('scale',None)
            if scale_factor is None and hasattr(data[p]['data'],'__dict__') : scale_factor=data[p]['data'].__dict__.get('scale_factor',None)  
            if scale_factor is None and hasattr(data[p]['data'],'__dict__') : scale_factor=data[p]['data'].__dict__.get('scale',None) 
            
            
            offset=data[p].get('add_offset',None) 
            if offset is None and hasattr(data[p]['data'],'__dict__') : offset=data[p]['data'].__dict__.get('add_offset',None)
            
            #Apply scaling and prepare message
            scale_msg='Apply scaling : {}'.format(p)
            if scale_factor is not None :
                data[p]['data'] = data[p]['data'] / scale_factor
                scale_msg+=' / {0}'.format(scale_factor)
            if offset is not None :
                data[p]['data'] = data[p]['data'] - offset
                scale_msg+=' - {0}'.format(offset)
            
            #show message
            if scale_factor is not None or offset is not None :
                self.message(2,scale_msg)
            
            #Apply fill_value as argument to createVariable function
            if hasattr(data[p]['data'],'fill_value') :
                locals()[p] = root_grp.createVariable(p,
                                               data[p]['data'].dtype if not str(data[p]['data'].dtype).startswith('|S') else 'S1',
                                               pardim,
                                               fill_value=data[p]['data'].fill_value)
            else :
                locals()[p] = root_grp.createVariable(p,
                                               data[p]['data'].dtype if not str(data[p]['data'].dtype).startswith('|S') else 'S1',
                                               pardim)
            
            #Get data and compare to current dimensions
            dumVar=data[p].pop('data')
            ncsh=tuple([long(dimVal[dimlist.index(d)]) for d in pardim if d in dimlist])
            ncdimname=tuple([d for d in pardim if d in dimlist])
            
            #Transposition is done if provided dimensions is not in phase with data dimensions (and if provided dimensions has no unlimited dimensions)
            if not ncsh == dumVar.shape and ncsh.count(0) == 0 :
                dimOrder=tuple([ncsh.index(dsh) for dsh in dumVar.shape])
                self.message(2, 'Transposing data axes {0}{1}'.format(ncdimname,dimOrder)) #Make it a bit more explicit...
                dumVar=dumVar.transpose(dimOrder)
            
            #Transpose data before writing it into file
            locals()[p][:]=dumVar
            #.transpose(tuple(range(len(pardim))[::-1])) #old stuff
                
            #Update with attribute list
            attrDict=locals()[p].__dict__
            attrDict.update(data[p])
            [attrDict.pop(k) for k in  locals()[p].__dict__.keys()]
            
            
            #Get common attributes first
            attrDict.pop('_FillValue',None)
            locals()[p].setncatts(attrDict)
#            for a in attrDict :
#                if not hasattr(locals()[p],a) :
#                    locals()[p].setncattr(a,data[p][a])
        
        self.message(2, 'Closing file')
        root_grp.close()

        return True
        
        
    
    def read(self,file_pattern,**kwargs):
        '''
        Read data from a NetCDF file
        
        :parameter file_pattern: a file pattern to be globbed (:func:`glob.glob`) or a file list.
        :keyword kwargs: additional keywords to be passed to :meth:`altimetry.tools.nctools.nc.load` (eg. extracting a subset of the file)
        ''' 
        
        #Setup file list
        if isinstance(file_pattern, str) : ls = glob.glob(file_pattern)
        elif isinstance(file_pattern,np.ndarray) :
            ls = file_pattern.tolist()
            file_pattern = file_pattern[0]
        
        if len(ls) == 0 :
            self.Error('File pattern not matched : ' + file_pattern)
                
        self.filelist = [os.path.basename(i) for i in ls]
        self.filelist_count = [0] * len(self.filelist)
        enum = list(enumerate(ls))
        enum = zip(*enum)
        
        self.fid_list = np.array(enum[0])
        self.dirname = os.path.dirname(os.path.abspath(file_pattern))
        
        self.par_list = np.array([])
        self.dim_list = np.array([])
        self._dimensions = OrderedDict({'_ndims':0})
         
        #Loop over data files
        #####################
        for i in np.arange(len(self.fid_list)) :
            
            #Read data file
            ###############
            filename = os.path.join(self.dirname,self.filelist[i])
            self.message(1, "Loading " + os.path.basename(filename))
            
            res = self.load(filename, **kwargs) #read() function is specific of each class
            #self.update_dataset(res) #update class with loaded data
            
            #self.check_variables()
        
        #self.update()

        return(res)

    def load(self, filename, params=None, force=False, depthrange=None, timerange=None, output_is_dict=True, **kwargs):
        """
        NetCDF data loader
        
        :parameter filename: file name
        :parameter params: a list of variables to load (default : load ALL variables).
        
        :parameter depthrange: if a depth dimension is found, subset along this dimension.
        :parameter timerange: if a time dimension is found, subset along this dimension. 

        .. note:: using :attr:`altimetry.tools.nctools.limit` allows subsetting to a given region.

        :parameter kwargs: additional arguments for subsetting along given dimensions.
        
        .. note:: You can index along any dimension by providing the name of the dimensions to subsample along. Values associated to the provided keywords should be a length 2 or 3 tuple (min,max,<step>) (cf. :func:`altimetry.data.nctools.load_ncVar`).
        
        :keyword output_is_dict: data structures are dictionnaries (eg. my_hydro_data.variable['data']). If false uses an object with attributes (eg. my_hydro_data.variable.data). 
        
        :return  {type:dict} outStr: Output data structure containing all recorded parameters as specificied by NetCDF file PARAMETER list.
        
        :author: Renaud Dussurget
        

        """
        
        if (params is not None) & isinstance(params,str): params=[params]
        
        #Open file
        self._filename = filename
        try:
            ncf = ncfile(self._filename, "r")
        except Exception,e:
            warn(repr(e),stacklevel=2)
            return {}
        
        #Load global attributes
        akeys = ncf.ncattrs()
        attrStr=OrderedDict()
        for A in akeys : attrStr.update({A:ncf.getncattr(A)})
     
        #Get list of recorded parameters:
        dum = ncf.variables.keys()
        nparam = np.shape(dum)[0]
    #        par_list=np.array([''.join(ncf.variables.keys()[0,i,:].compressed()) for i in np.arange(nparam)])
        par_list = np.array(['{0}'.format(v) for v in ncf.variables.keys()])
        
        #remove empty items and update nparam
        par_list = par_list.compress([len(par) != 0 for par in par_list])
        nparam = par_list.size
        
        if nparam == 0 : self.Error('File has no data ({0})'.format(self._filename))
        
        #Get dimensions
        ncdimlist = np.array(['{0}'.format(d) for d in ncf.dimensions.keys()])
        ndims = len(ncdimlist)
        dimStr = OrderedDict()
        dimStr.update({'_ndims':ndims})
    
        if ndims == 0 : self.Error('File has no dimensions ({0})'.format(self._filename))
        
        #Check for the presence of strategic dimensions
        checkedDims = np.array(['lon', 'lat', 'time', 'depth'])
        existDim = -np.ones(4,dtype=int)
        if not self.use_local_dims :
            for i,d in enumerate(ncdimlist) :
                if ( (d.lower().startswith('lon')) | (d.lower().find('longitude') != -1) ) & (d.find('LatLon') ==-1) : existDim[0]=i
                if ( (d.lower().startswith('lat')) | (d.lower().find('latitude') != -1) ) & (d.find('LatLon') ==-1): existDim[1]=i
                if (d.lower().startswith('time')) | (d.lower().startswith('date')) : existDim[2]=i
                if (d.lower().startswith('lev')) | (d.lower().startswith('dep')) : existDim[3]=i
                    
#            existDim[0] = np.where([d.lower().startswith('lon') | (d.lower().find('longitude') != -1) for d in ncdimlist])[0]
#            existDim[1] = np.where([d.lower().startswith('lat') | (d.lower().find('latitude') != -1) for d in ncdimlist])[0]
#            existDim[2] = np.where([(d.lower().startswith('time')) | (d.lower().startswith('date')) for d in ncdimlist])[0]
#            existDim[3] = np.where([(d.lower().startswith('lev')) | (d.lower().startswith('dep')) for d in ncdimlist])[0]
        
        identified = existDim > -1
        
#        checkedDims[identified]=checkedDims[identified][existDim.compress(identified).astype(int)]
#        checkedDims=checkedDims[identified]
        
#        for cn, vn in enumerate(checkedDims) : dimStr.update({cn:len(ncf.dimensions[vn])})
        
        #Update dimension structure with identified dimensions
        #Load dimensional variables
        #TODO : Add scaling here in case...
        for i,d in enumerate(existDim) : 
            if identified[i] :
                dimStr.update({ncdimlist[d]:len(ncf.dimensions[ncdimlist[d]])}) #Append dimension
                cmd =  'load_ncVar(\'' + ncdimlist[d] + '\',nc=ncf)'
                self.message(4, 'loading : {0}={1}'.format(checkedDims[i],cmd))
                locals()[checkedDims[i]]=load_ncVar(ncdimlist[d], nc=ncf,**kwargs)

        missdims=set(ncdimlist)
        missdims.difference_update(ncdimlist[existDim[identified]])
        missdims=list(missdims)

        for i,d in enumerate(missdims) :
            dimStr.update({d:len(ncf.dimensions[d])})
            if ncf.variables.has_key(d) :
                cmd = 'load_ncVar(\'' + d + '\',nc=ncf)'
                self.message(4, 'loading : {0}={1}'.format(d,cmd))
                locals()[d]=load_ncVar(d, nc=ncf,**kwargs)
                        
            #If the variable associated to the dimension do not exist, generate it
            else :
                self.message(1, '[WARNING] Netcdf file not standard - creating data for {0} dimnsion'.format(d))
                ndim=len(ncf.dimensions[d])
                cmd = '=var'
                self.message(4, 'loading : {0}={1}'.format(d,cmd))
                locals()[d]={'_dimensions':{'_ndims':1,d:ndim}, 'data':np.arange(ndim)}
        
#        #Update dimension structure with identified dimensions
#        for cn, vn in zip(*(checkedDims[identified], ncdimlist[identified])) : dimStr.update({cn:len(ncf.dimensions[vn])})
#        for vn in ncdimlist[~identified] : dimStr.update({vn:len(ncf.dimensions[vn])})
        
        
        #Load dimensional variables
        #TODO : Add scaling here in case...
#        for cn, vn in zip(*(checkedDims[identified], ncdimlist[identified])) :
##            cmd = 'self.'+cn+'=ncf.variables[\''+vn+'\'][:]'
#            cmd = cn + '=load_ncVar(\'' + vn + '\',nc=ncf)'
#            self.message(4, 'exec : ' + cmd)
#            exec(cmd)
#            
#        for vn in ncdimlist[~identified] :
##            cmd = 'self.'+vn+'=ncf.variables[\''+vn+'\'][:]'
#            cmd = vn + '=load_ncVar(\'' + vn + '\',nc=ncf)'
#            self.message(4, 'exec : ' + cmd)
#            exec(cmd)
            
        #Update dimlist with dimensions present in the object
#        dimlist = np.append(checkedDims[identified], ncdimlist[~identified])

        dimlist=ncdimlist.copy()
#        dimlist[existDim[identified]]=checkedDims[identified]
        if identified.sum() > 0 : dimlist[existDim[identified]]=checkedDims[identified]
        else : dimlist = dimlist[[]]
        
#        for d in ncdimlist[checkedDims[identified]] :
#            if not d.startswith('_') : dimlist = np.append(dimlist,d)
#        dimlist=[(d if not d.startswith('_') else None) for d in dimStr.keys()]
        
        if params is not None :
            if force : par_list = [i.upper() for i in params]
            else :par_list = list(set(params).intersection(par_list))
        else : par_list = par_list.tolist()
        
        #remove dimensional  variable
        for d in ncdimlist[existDim[identified]] :
            par_list.pop(par_list.index(d))
        
        self.message(2, 'Recorded parameters : ' + str(nparam) + ' -> ' + str(par_list))
     
        
        #Extract within limits
        if (existDim[0] > -1) & (existDim[1] > -1):
            llind, flag = in_limits(lon['data'],lat['data'], limit=self.limit)
            if isinstance(flag,tuple) :
                lon['data'] = recale(lon['data'].compress(flag[0]),degrees=True)
                lon['_dimensions'][lon['_dimensions'].keys()[1]] = flag[0].sum()
                lat['data'] = lat['data'].compress(flag[1])
                lat['_dimensions'][lat['_dimensions'].keys()[1]] = flag[1].sum()
            else :
                lon['data'] = recale(lon['data'].compress(flag),degrees=True)
                lon['_dimensions'][lon['_dimensions'].keys()[1]] = flag.sum()
                lat['data'] = lat['data'].compress(flag)
                lat['_dimensions'][lat['_dimensions'].keys()[1]] = flag.sum()
            
            locals()[ncdimlist[existDim[0]]]=lon.copy()
            locals()[ncdimlist[existDim[1]]]=lat.copy()
            
            dimStr.update({ncdimlist[existDim[0]]:len(lon['data'])})
            dimStr.update({ncdimlist[existDim[1]]:len(lat['data'])})
#            self.message(4, 'self.lon & self.lat updated')
        
        if (existDim[2] > -1):
            if (timerange is not None) : timeflag = (time['data'] >= np.min(timerange)) & (time['data'] <= np.max(timerange))
            else : timeflag = np.ones(len(time['data']), dtype=bool)
            if timeflag.sum() == 0 : self.Error('No data within specified depth range (min/max = {0}/{1})'.format(np.min(time), np.max(time)))
            time['data'] = time['data'].compress(timeflag)
            time['_dimensions'][time['_dimensions'].keys()[1]] = timeflag.sum()
            locals()[ncdimlist[existDim[2]]]=time.copy()
            dimStr.update({ncdimlist[existDim[2]]:len(time['data'])})
#            self.message(4, 'self.lon & self.lat updated')
        
        #Extract within depth range
        if (existDim[3] > -1):
            if (depthrange is not None) : depthflag = (depth['data'] >= np.min(depthrange)) & (depth['data'] <= np.max(depthrange))
            else : depthflag = np.ones(len(depth['data']), dtype=bool)
            if depthflag.sum() == 0 : self.Error('No data within specified depth range (min/max = {0}/{1})'.format(np.min(depth), np.max(depth)))
            depth['data'] = depth['data'].compress(depthflag)
            depth['_dimensions'][depth['_dimensions'].keys()[1]] = depthflag.sum()
            locals()[ncdimlist[existDim[3]]]=depth.copy()
            dimStr.update({ncdimlist[existDim[3]]:len(depth['data'])})
        
        #Create output data structure
        outStr = OrderedDict()
        outStr.update({'_dimensions':dimStr})
        outStr.update({'_attributes':attrStr})
        
        if (existDim[0] > -1) : outStr.update({ncdimlist[existDim[0]]:lon})
        if (existDim[1] > -1) : outStr.update({ncdimlist[existDim[1]]:lat})
        if (existDim[2] > -1) : outStr.update({ncdimlist[existDim[2]]:time})
        if (existDim[3] > -1) : outStr.update({ncdimlist[existDim[3]]:depth})
        
        
        #Update object with remaining variables
        for d in dimlist.compress([not outStr.has_key(f) for f in dimlist]) :
#            cmd = 'outStr.update({\''+d+'\':'+d+'[\'data\']})'
            cmd = 'outStr.update({\''+d+'\':'+d+'})'
            self.message(4, 'exec : '+cmd)
            exec(cmd)
        
        ncdimStr=outStr.copy()
        #Get dimension lengths
        shape=()
        for d in dimlist: shape += np.shape(locals()[d]['data'])
        
        ndims = np.size(shape)
     
#        #Create dimension structure
#        curDim = [str(dimname) for dimname in dimStr.keys()[1:]] #[str(dimname) for dimname in ncf.variables['LONGITUDE'].dimensions]
#        curDimval = [dimStr[dim] for dim in curDim] #[len(ncf.dimensions[dimname]) for dimname in curDim]
#   
#        outStr={'_dimensions':{'_ndims':ndims,'nbpoints':sz[0]},'lon':lon,'lat':lat,'date':date}
        
#        for d in dimlist : outStr.update({d:self.__dict__[d]})

        #Sort NCDIMLIST to match DIMLIST
#        ncdimlist[np.sort(existDim.astype(np.int)[identified])]=ncdimlist[existDim[identified].tolist()]

        #Setup kwargs with current dimensionnal properties
        for d, ncd in zip(*(dimlist,ncdimlist)):
            if not kwargs.has_key(ncd) :
                if kwargs.has_key(d) :
                    
                    kwargs.update({ncd:kwargs[d]})
                    del kwargs[d]
                else :
                    dvar=ncdimStr[d]['data']
                    if isinstance(dvar,np.ma.masked_array) : kwargs.update({ncd:(np.nanmin(dvar.data),np.nanmax(dvar.data))})
                    else : kwargs.update({ncd:(np.nanmin(dvar),np.nanmax(dvar))})
#            else :
#                outStr['NbLatitudes']['data']        
        for param in par_list :
#            dumVar = load_ncVar(param,  nc=ncf, lon=llind[0], lat=llind[1], time=np.arange(len(time['data'])).compress(timeflag),**kwargs) #Load variables
#            dumVar = load_ncVar(param,  nc=ncf, longitude=(self.limit[1],self.limit[3]), latitude=(self.limit[0],self.limit[2]), time=(self.time.min(),self.time.max()),**kwargs) #Load variables
            
            
            dumVar = load_ncVar(param,  nc=ncf, **kwargs) #Load variables
#            dimStr = dumVar['_dimensions']
            
            #update dimensions
#            curDim = [str(dimname) for dimname in dimStr.keys()[1:]] #[str(dimname) for dimname in ncf.variables['LONGITUDE'].dimensions]
#            curDimval = [dimStr[dim] for dim in curDim] #[len(ncf.dimensions[dimname]) for dimname in curDim]
            
#            curDim = dimlist[where_list(curDim, ncdimlist.tolist())] #Convert to object dimension names
#            curDim = dimlist[where_list(curDim, dimlist.tolist())] #Convert to object dimension names (???)
            
##            curDim = [str(dimname) for dimname in ncf.variables[param].dimensions]
##            curDimval = [len(ncf.dimensions[dimname]) for dimname in curDim]
#            flag = [(np.array(dimname) == outStr['_dimensions'].keys()).sum() == 0 for dimname in curDim] #find dimensions to update
#            dimUpdate = np.array(curDim).compress(flag)
#            for enum in enumerate(dimUpdate) : 
#                self.message(2, 'Appending dimensions {0}:{1} to dataStructure'.format(enum[1], np.array(curDimval).compress(flag)[enum[0]]))
#                outStr['_dimensions'].update({enum[1]:np.array(curDimval).compress(flag)[enum[0]]}) #Append new dimension
#                outStr['_dimensions']['_ndims'] += 1 #update dimension counts
            
#            cmd = 'dumStr = {\'' + param + '\':dumVar[\'data\']}'


            #Set list as variable with attributes
#            if (not output_is_dict):
#                var=dumVar.pop('data')
#                for k in dumVar.keys():
#                    setattr(var, k, dumVar.pop(k))
#                dumVar=var.copy()
            
            cmd = 'dumStr = {\'' + param + '\':dumVar}'
            self.message(4, 'exec : ' + cmd)
            exec(cmd)
            outStr.update(dumStr)
            
            #Update output dimensions with extracted dimensions
            for ddum in dumStr[param]['_dimensions'].keys()[1:] :
                if outStr['_dimensions'].get(ddum) != dumStr[param]['_dimensions'][ddum] : outStr['_dimensions'][ddum]=dumStr[param]['_dimensions'][ddum]
            
#            cmd = 'self.'+param+'='
        
        ncf.close()
        return outStr
    
    def message(self, MSG_LEVEL, str):
        """
        print function wrapper. Print a message depending on the verbose level
        
        :param {in}{required}{type=int} MSG_LEVEL: level of the message to be compared with self.verbose
        
        :example: display a message
           
           .. code-block:: python
           
              self.log(0,'This message will be shown for any verbose level')
           
        :author: Renaud DUSSURGET (RD), LER PAC/IFREMER
        :change: Added a case for variables with missing dimensions
         
        """
        caller=get_caller()
        if MSG_LEVEL <= self.verbose : print('[{0}.{1}()] {2}'.format(__name__,caller.co_name,str))
        
    def Error(self, ErrorMsg):    
        raise Exception(ErrorMsg)
    
    def attributes(self, filename, **kwargs):
        """
        Get attributes of a NetCDF file
        
        :return {type:dict} outStr: Attribute structure.
        :author: Renaud Dussurget
        """
        
        #Open file
        self._filename = filename
        ncf = ncfile(self._filename, "r")
     
        #Get list of recorded parameters:
        keys = ncf.__dict__.keys()
        outStr = OrderedDict()
        for a in keys: outStr.update({a:ncf.__getattr__(a)})

        return outStr
        

def load_ncVar(varName, nc=None, **kwargs):
        '''
        Loads a variable from the NetCDF file and saves it as a data structure.
        
        :parameter varName: variable name
        :keywords kwargs: additional keyword arguments for slicing the dataset. Keywords should be named the name of the dimensions to subsample along and associated value should be a length 2 or 3 tuple (min,max,<step>).
        
        .. note: slices are provided in this interval : [min,max] (ie. including both extremities)
        
        '''
        
        if (nc is None) : raise Exception('No Netcdf file passed')
        
        var = nc.variables[varName]
        
        var.set_auto_maskandscale(False)
        
        #Load dimensions
        varDim = [str(dim) for dim in var.dimensions]
        missDim=len(varDim) == 0
        if (missDim):
            warn('No dimension found - creating it')
            sh=var[:].shape
            varDimval = sh
            varDim = ['dim_%02i' % (i+1) for i in xrange(len(varDimval))]
        else : varDimval = [len(nc.dimensions[dimname]) for dimname in varDim]
        
        #Load Attributes
        attrStr=var.__dict__
        
        ind_list = [] #Init index list
        dims = OrderedDict({'_ndims':0}) #Init dimensions
        
        dstr=[]
        shape=()

        #Construct index list
        #looping on variable dimension list
        for vid,vn in enumerate(varDim) :
            
            #No indexation on current dimension
            if not kwargs.has_key(vn) :
                dstr=np.append(dstr,':')
                sz=np.long(varDimval[vid])
#                ind_list.append(range(varDimval[vid])) # if no restriction in kargs then equivalent to [:]
#                dims.update({vn:varDimval[vid]})
            
            #Data is indexed along current dimension
            else :
                drange=kwargs[vn]
                if len(drange) == 2 : drange = drange + (1,)
                if nc.variables.has_key(vn) : #Check if current dimension exists
                    dumvar = nc.variables[vn][:]
                else :
                    dumvar = np.arange(len(nc.dimensions[vn]))
                if vn.startswith('lon') : dumvar=recale(dumvar,degrees=True)
                fg=(dumvar >= drange[0]) & (dumvar <= drange[1])
                if fg.sum() == 0 :
                    #retry switrhcing lon/lat
                    dumvar=recale(dumvar,degrees=True)
                    drange=tuple(recale(drange,degrees=True))#.astype(np.long))
                    fg=(dumvar >= drange[0]) & (dumvar <= drange[1])
                if fg.sum() == 0 :
                    raise IndexError('{0} {1} is not matching given dimensions {2}'.format(vn,(np.nanmin(nc.variables[vn][:]),np.nanmax(nc.variables[vn][:])),drange))
                if len(fg) == 1 :
                    dstr=np.append(dstr,':')
                    sz=1L
                elif len(fg) == 0:
                    sz=0L
                else :
                    dumind=np.arange(varDimval[vid],dtype=long).compress(fg)
                    bg=dumind[0]
                    en=dumind[-1]+1
                    st=long(drange[2])
                    dstr=np.append(dstr,'{0}:{1}:{2}'.format(bg,en,st))
                    sz = np.long(np.mod(np.float(en-bg-1)/st,np.float(en-bg)) + 1.)
            
            dims.update({vn:sz})
            shape = shape + (sz,)
#                if isinstance(dumind, np.ndarray) : dumind = dumind.tolist() #Rq: tolist() can take a very long time to run on large arrays
#                if type(dumind) is not list : dumind = [dumind] 
#                ind_list.append(dumind)
#                dims.update({vn:len(dumind)})
        
#        #check index list
#        sz = [np.size(i) for i in ind_list]
        
        dstr=','.join(dstr) #invert dimension list for numpy
#        dstr=','.join(dstr[::-1]) #invert dimension list for numpy
        if missDim : cmd = 'varOut = var[:]'
        else : cmd = 'varOut = var[{0}]'.format(dstr)
        exec(cmd)
        
        #find empty variables
#        if not (atools.where_list([0], shape)[0] == -1) : varOut = var[[0]][[]]
#        else : varOut = var[ind_list]
        
        #Mask it!
        if var.__dict__.has_key('_FillValue') :
            fill_value=var._FillValue
            mask = varOut == var._FillValue
        elif var.__dict__.has_key('missing_value') :
            fill_value=var._FillValue
            mask = varOut == var._FillValue
        else :
            fill_value = None
            mask = np.zeros(varOut.shape, dtype='bool')
        
        #Scale it
        #note : we do not use the *= or += operators to force casting to scaling attribute types
        if var.__dict__.has_key('scale') : varOut = varOut * var.scale
        elif var.__dict__.has_key('scale_factor') : varOut = varOut * var.scale_factor
        if var.__dict__.has_key('add_offset') : varOut = varOut + var.add_offset
        
        #Set masks properly
        if isinstance(varOut, np.ndarray) : varOut = np.ma.masked_array(varOut, mask=mask,dtype=varOut.dtype,fill_value=fill_value)
        elif isinstance(varOut, np.ma.masked_array) : var.mask = mask
        else : raise 'This data type {} has not been defined - code it!'.format(type(varOut))
        
        #Update masked data properly
        varOut.data[varOut.mask]=varOut.fill_value
        
        #Switch dimensions 
        if not missDim : varOut=np.transpose(varOut,tuple(range(len(dims.keys()[1:]))[::-1]))
        
        #Build up output structure
        dims.update({'_ndims':len(dims.keys()[1:])})
        outStr = {'_dimensions':dims, 'data':varOut}
        
        #Add variable attributes
        for A in var.__dict__.keys():
            outStr[A]=var.getncattr(A)
        
        return outStr
#            ind_list=[[]] 
    
#Additional functions
def load_ncVar_v2(varName,nc=None,**kwargs):
        
        if nc is None : raise 'No Netcdf file passed'
        
        #Load variable
        var = nc.variables[varName]
        
        var.set_auto_maskandscale(False)
        
        #Load dimensions
        varDim = [str(dim) for dim in var.dimensions]
        varDimval = [len(nc.dimensions[dimname]) for dimname in varDim]
        
        #Load Attributes
        attrStr=var.__dict__
        
#        from collections import deque
        ind_list = [] #deque() #Init index list
        dims={'_ndims':0} #Init dimensions

        #Construct index list
        #looping on variable dimension list
        for enum in enumerate(varDim) :
            
            #No indexation on current dimension
            if not kwargs.has_key(enum[1]) :
#                ind_list+=tuple(xrange(varDimval[enum[0]]))
                ind_list.append(xrange(varDimval[enum[0]]))
#                ind_list=(ind_list,xrange(varDimval[enum[0]])) if len(ind_list) != 0 else (xrange(varDimval[enum[0]]),)
#                .append(xrange(varDimval[enum[0]])) # if no restriction in kargs then equivalent to [:]
                dims.update({enum[1]:varDimval[enum[0]]})
            
            #Data is indexed along current dimension
            else :
                dumind = kwargs[enum[1]]
#                if not isinstance(dumind,list) : dumind=tuple(dumind)
                if isinstance(dumind,np.ndarray) : dumind=dumind.tolist() #Rq: tolist() can take a very long time to run on large arrays
                if type(dumind) is not list : dumind=[dumind] 
                ind_list.append(dumind)
#                ind_list=(ind_list,dumind)  if len(ind_list) != 0 else (dumind,)
                dims.update({enum[1]:len(dumind)})
        
        #check index list
        sz=[len(i) for i in ind_list]
        
        #find empty dimensions
        if not (where_list([0],sz)[0] == -1 ) : varOut=var[[0]][[]] #np.array(where_list(sz,[0])) == -1
        else :
            varOut=var[ind_list]#.copy() #THIS IS LONG!!
            if var.shape == (1,1) : varOut=varOut.reshape(var.shape)
        
        #Mask it!
        if var.__dict__.has_key('_FillValue') : mask=varOut == var._FillValue
        elif var.__dict__.has_key('missing_value') : mask=varOut == var.missing_value
        else : mask=np.zeros(varOut.shape,dtype='bool')
        
        #Scale it
        #note : we do not use the *= or += operators to force casting to scaling attribute types
        if var.__dict__.has_key('scale') : varOut =varOut * var.scale
        elif var.__dict__.has_key('scale_factor') : varOut = varOut * var.scale_factor
        if var.__dict__.has_key('add_offset') : varOut = varOut + var.add_offset
        
        #Set masks properly
        if isinstance(varOut,np.ndarray) : varOut=np.ma.masked_array(varOut,mask=mask)
        elif isinstance(varOut,np.ma.masked_array) : var.mask=mask
        else : raise 'This data type {} has not been defined - code it!'.format(type(varOut))
        
        #Get attributes
        attrStr=var.__dict__
        attrStr.pop('_FillValue',None) #Remove this attributed as it is overidden
        
        #Append attributes to varOut
        varOut.__dict__.update(attrStr)
        
        #Build up output structure
        outStr={'_dimensions':dims,'data':varOut}
        outStr.update({'_attributes':attrStr})
        dims.update({'_ndims':len(dims.keys()[1:])})
        
        return outStr
##            ind_list=[[]] 
