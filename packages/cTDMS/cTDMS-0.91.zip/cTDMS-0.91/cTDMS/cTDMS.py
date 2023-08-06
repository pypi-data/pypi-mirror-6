# -*- coding: utf-8 -*-

__version__  = '0.91'
__date__     = '$Date: 2014-03-24 22:00:00'

__all__=["DDC_UInt8", "DDC_Int16",  "DDC_Int32",  "DDC_Float",  "DDC_Double",  \
                "DDC_String",  "DDC_Timestamp",  \
                "Attrs",  "TDM_File",  "TDM_Group",  "TDM_Channel"]

"""  Module cTDMS
    Version 0.91
    Changes in 0.91:    adaption for Python 64 bit (thanks to Charles Briere)
    
    cTDMS is a ctypes based module, which serves to read or write files 
    in the TDM or TDMS format, which is a file format introduced by 
    National Instruments
"""
import datetime

import os.path
from os import getcwd,  chdir
import ctypes as CT

import numpy as NP
from numpy.ctypeslib import as_ctypes,  ndpointer

# change to Path, where the NI dlls are and load the nilibddc
ni_path,_file=os.path.split(__file__)
c_path=getcwd()
chdir(ni_path)
try: 
    NI = CT.WinDLL("nilibddc")
except Exception,  ex:
    print("Exception: %s \ncTDMS cannot find the NILIBDDC.DLL"%(ex))
    exit()   
chdir(c_path)

DDC_File=1
DDC_Group=2
DDC_Channel=3

DDC_UInt8		= 5 # unsigned char
DDC_Int16		= 2 #  short
DDC_Int32		= 3 #  int
DDC_Float		= 9 #  float
DDC_Double		= 10 #  double
DDC_String		= 23 #  string
DDC_Timestamp	= 30 #  timestamp (Year/Month/Day/Hour/Minute/Second/Millisecond components)

DDC_Types={5: "UInt8",  2:"Int16",  3:"Int32",  9:"Float", 10:"Double",  23:"String",  30:"Timestamp"}
# Mapping of DDC types to ctypes
DDC_ctypes={DDC_UInt8:CT.c_uint8,  DDC_Int16:CT.c_int16,  DDC_Int32:CT.c_int32, DDC_Float:CT.c_float,  DDC_Double:CT.c_double,   DDC_String:None,  DDC_Timestamp:None}
Numpy_Types={DDC_UInt8:"u1",  DDC_Int16:"i2",  DDC_Int32:"i4",  DDC_Float:"float32",  DDC_Double:"float64"}
Attr_functions={DDC_File:[NI.DDC_SetFilePropertyUInt8,  NI.DDC_SetFilePropertyInt16 ,  NI.DDC_SetFilePropertyInt32 ,  NI.DDC_SetFilePropertyFloat , 
                              NI.DDC_SetFilePropertyDouble ,  NI.DDC_SetFilePropertyString,  NI.DDC_SetFilePropertyTimestampComponents, 
                              NI.DDC_CreateFilePropertyUInt8,  NI.DDC_CreateFilePropertyInt16 ,  NI.DDC_CreateFilePropertyInt32 ,  NI.DDC_CreateFilePropertyFloat , 
                              NI.DDC_CreateFilePropertyDouble ,  NI.DDC_CreateFilePropertyString,  NI.DDC_CreateFilePropertyTimestampComponents
                              ], 
                DDC_Group:[NI.DDC_SetChannelGroupPropertyUInt8,  NI.DDC_SetChannelGroupPropertyInt16 ,  NI.DDC_SetChannelGroupPropertyInt32 ,  NI.DDC_SetChannelGroupPropertyFloat , 
                              NI.DDC_SetChannelGroupPropertyDouble ,  NI.DDC_SetChannelGroupPropertyString,  NI.DDC_SetChannelGroupPropertyTimestampComponents, 
                              NI.DDC_CreateChannelGroupPropertyUInt8,  NI.DDC_CreateChannelGroupPropertyInt16 ,  NI.DDC_CreateChannelGroupPropertyInt32 ,  NI.DDC_CreateChannelGroupPropertyFloat , 
                              NI.DDC_CreateChannelGroupPropertyDouble ,  NI.DDC_CreateChannelGroupPropertyString,  NI.DDC_CreateChannelGroupPropertyTimestampComponents
                              ], 
                DDC_Channel:[NI.DDC_SetChannelPropertyUInt8,  NI.DDC_SetChannelPropertyInt16 ,  NI.DDC_SetChannelPropertyInt32 ,  NI.DDC_SetChannelPropertyFloat , 
                              NI.DDC_SetChannelPropertyDouble ,  NI.DDC_SetChannelPropertyString,  NI.DDC_SetChannelPropertyTimestampComponents, 
                              NI.DDC_CreateChannelPropertyUInt8,  NI.DDC_CreateChannelPropertyInt16 ,  NI.DDC_CreateChannelPropertyInt32 ,  NI.DDC_CreateChannelPropertyFloat , 
                              NI.DDC_CreateChannelPropertyDouble ,  NI.DDC_CreateChannelPropertyString,  NI.DDC_CreateChannelPropertyTimestampComponents
                              ], 
                }
DDC_SetUInt8=0
DDC_SetInt16=1
DDC_SetInt32= 2
DDC_SetFloat = 3
DDC_SetDouble= 4
DDC_SetString= 5
DDC_SetTimestampComponents= 6
DDC_CreateUInt8= 7
DDC_CreateInt16 = 8
DDC_CreateInt32 = 9
DDC_CreateFloat = 10
DDC_CreateDouble =11
DDC_CreateString= 12
DDC_CreateTimestampComponents=13


DDC_FILE_NAME="name"				# Name
DDC_FILE_DESCRIPTION="description"		# Description
DDC_FILE_TITLE="title"				# Title
DDC_FILE_AUTHOR="author"			# Author
DDC_FILE_DATETIME="datetime"			# Date/Time

# ChannelGroup property constants
DDC_CHANNELGROUP_NAME="name"				# Name
DDC_CHANNELGROUP_DESCRIPTION="description"		# Description

# Channel property constants
DDC_CHANNEL_NAME="name"				# Name
DDC_CHANNEL_DESCRIPTION="description"		# Description
DDC_CHANNEL_UNIT_STRING="unit_string"		# Unit String
DDC_CHANNEL_MINIMUM="minimum"			# Minimum
DDC_CHANNEL_MAXIMUM="maximum"			# Maximum



class Attrs(object):
    def __init__(self, fgc,  handle):
        self.handle=handle
        self.fgc=fgc
        if fgc==DDC_File:
            self.getNum=NI.DDC_GetNumFileProperties
            self.getNames=NI.DDC_GetFilePropertyNames
            self.getType=NI.DDC_GetFilePropertyType
            self.getProperty=NI.DDC_GetFileProperty
            self.getTimestamp=NI.DDC_GetFilePropertyTimestampComponents
            self.getStringLength=NI.DDC_GetFileStringPropertyLength
            self.setProperty=NI.DDC_SetFileProperty 
            self.createProperty=NI.DDC_CreateFileProperty 
            self.exists=NI.DDC_FilePropertyExists
        elif fgc==DDC_Group:
            self.getNum=NI.DDC_GetNumChannelGroupProperties
            self.getNames=NI.DDC_GetChannelGroupPropertyNames
            self.getType=NI.DDC_GetChannelGroupPropertyType
            self.getProperty=NI.DDC_GetChannelGroupProperty
            self.getTimestamp=NI.DDC_GetChannelGroupPropertyTimestampComponents
            self.getStringLength=NI.DDC_GetChannelGroupStringPropertyLength
            self.setProperty=NI.DDC_SetChannelGroupProperty 
            self.createProperty=NI.DDC_CreateChannelGroupProperty 
            self.exists=NI.DDC_ChannelGroupPropertyExists
        else:
            self.getNum=NI.DDC_GetNumChannelProperties
            self.getNames=NI.DDC_GetChannelPropertyNames
            self.getType=NI.DDC_GetChannelPropertyType
            self.getProperty=NI.DDC_GetChannelProperty
            self.getTimestamp=NI.DDC_GetChannelPropertyTimestampComponents
            self.getStringLength=NI.DDC_GetChannelStringPropertyLength
            self.setProperty=NI.DDC_SetChannelProperty 
            self.createProperty=NI.DDC_CreateChannelProperty 
            self.exists=NI.DDC_ChannelPropertyExists
        self.attrs=dict()
        self.attrs_type=dict()
        
        # get number, how many attributes
        noP=CT.c_uint(0)
        ddc_ck(self.getNum (self.handle, CT.byref(noP)))
    
        #get names of the attributes
        propertyNames=(CT.c_char_p*noP.value)()
        pp=CT.pointer(propertyNames)
        ddc_ck(self.getNames(self.handle, pp, noP))
        
        # get types/values of the attributes
        dataType=CT.c_int()
        val=CT.c_int(0)
        for i in range(0, noP.value):
            name=CT.string_at(propertyNames[i])
            ddc_ck(self.getType(self.handle,  name,  CT.byref(dataType)))
            
            if dataType.value in [DDC_Double,  DDC_Float]:
                val=CT.c_double(0.0)
                ddc_ck(self.getProperty(self.handle,  name,  CT.byref(val),  0))
            elif dataType.value==DDC_String:
                length=CT.c_uint()
                ddc_ck(self.getStringLength(self.handle, name,  CT.byref(length)))
                length=length.value+1
                val=CT.create_string_buffer(length)
                ddc_ck(self.getProperty(self.handle,  name,  val,  length))
            elif dataType.value in [DDC_UInt8,  DDC_Int16,  DDC_Int32]:
                val=CT.c_int(0)
                ddc_ck(self.getProperty(self.handle,  name,  CT.byref(val),  0))
            elif dataType.value==DDC_Timestamp:
                val=Timestamp()
                ddc_ck(self.getTimestamp(self.handle,  name,  CT.byref(val.year),  CT.byref(val.month),  
                        CT.byref(val.day),   CT.byref(val.hour) ,  CT.byref(val.minute),  CT.byref(val.second),  CT.byref(val.millisecond),
                        CT.byref(val.weekday)))
                val.set_value()
                
            self.attrs[name]=val.value
            self.attrs_type[name]=dataType.value
    
    def __contains__(self,  item):
        return item in self.attrs
    
    def __len__(self):
        return len(self.attrs)
        
    def __iter__(self):
        return self.attrs.__iter__()
            
    def __getitem__(self,  item):
        if item in self.attrs:
            return self.attrs[item]
        raise KeyError("%s is no property"%(item))
        
    def get(self,  item,  default):
        if item in self.attrs:
            return self.attrs[item]
        return default
    
    def __setitem__(self, item,  data):
        # get the right functions set
        functions=Attr_functions[self.fgc]
        c_item=CT.c_char_p(str(item))
        #  overwrite existing attribute
        if item in self.attrs:
            self.attrs[item]=data     # copy the data to the cache (self.attrs)
            # convert to correct data type and self.setProperty
            attr_type=self.attrs_type[item]
            # and write the data to the TDMS file
            if attr_type==DDC_String:
                #Todo check for unicode
                data=CT.c_char_p(str(data))
                # setPropertyString =
                ret=functions[DDC_SetString]  (self.handle, c_item,  data)
            elif attr_type==DDC_Timestamp:
                if type(data) == datetime.datetime:
                    millisecond=CT.c_double(data.microsecond*1000)
                    ret=functions[DDC_SetTimestampComponents](self.handle,  c_item,  data.year,  data.month,  data.day,  data.hour,  data.minute,  data.second,  millisecond)

#{DDC_UInt8:c_uint8,  DDC_Int16:c_int16,  DDC_Int32:c_int32, DDC_Float:c_float,  DDC_Double:c_double,   DDC_String:None,  DDC_Timestamp:None}
            elif attr_type==DDC_UInt8:
                data=CT.c_uint8(data)
                functions[DDC_SetUInt8](self.handle, c_item,  data)
            elif attr_type==DDC_Int16:
                data=CT.c_int16(data)
                functions[DDC_SetInt16](self.handle, c_item,  data)
            elif attr_type==DDC_Int32:
                data=CT.c_int32(data)
                functions[DDC_SetInt32](self.handle, c_item,  data)
            elif attr_type==DDC_Float:
                data=CT.c_float(data)
                functions[DDC_SetFloat](self.handle, c_item,  data)
            elif attr_type==DDC_Double:
                data=CT.c_double(data)
                functions[DDC_SetDouble](self.handle, c_item,  data)
        else:
            # create new property
            self.attrs[item]=data   # copy the data to the cache (self.attrs)
           
            # check the type of data
            # and create a new attribute/property in the TDMS file
            if type(data) in [long,  int]:
                attr_type=DDC_Int32
                data=CT.c_int32(data)
                functions[DDC_CreateInt32](self.handle, c_item,  data)
            elif type(data)==float:
                attr_type=DDC_Double
                data=CT.c_double(data)
                functions[DDC_CreateDouble](self.handle, c_item,  data)
            elif isinstance(data,  basestring):
                attr_type=DDC_String
                #Todo unicode
                data_p=CT.c_char_p(str(data))
                ret=functions[DDC_CreateString]  (self.handle, c_item,  data_p)
            elif type(data)==datetime.datetime:
                attr_type=DDC_Timestamp
                # print "convert to Timestamp"
                if type(data) == datetime.datetime:
                    millisecond=CT.c_double(data.microsecond*1000)
                    ret=functions[DDC_CreateTimestampComponents](self.handle,  c_item,  data.year,  data.month,  
                                            data.day,  data.hour,  data.minute,  data.second,  millisecond)
                else:
                    raise ValueError()
                    
            self.attrs_type[item]=attr_type


    def __delitem__(self,  item):
        raise BaseExection("delete property not implemented")
#        del self.attrs[item]
#        del self.attrs_type[item]
        

        
class TDM_File(object):
    def __init__(self,   filename,  readonly=0,  
                 fileType="",  name="",  description="", title="", author=""):
        #filename must be in format "C:\\Daten\\Projekte\\PyVDAW\\tdms.tdms"
        #  filename=filename.replace("/",  "\\\\")
        self.readonly=CT.c_int8(readonly)
        self.filename=unicode(filename)
        self.fileType=fileType
        self.name=name
        self.description=description
        self.title=title
        self.author=author
#        self.filehandle=CT.c_int()
        self.filehandle=CT.POINTER(CT.c_int)()
        
    def __enter__(self):
        self.open()
        return self
       
    def __exit__(self,  exc_type,  exc_val,  exc_tb):
        if not self.readonly.value:
            self.save()
        self.close()
        
    def open(self):
        ufilename=CT.create_string_buffer(self.filename)
#        self.filehandle=CT.c_int()
        self.Groups=dict()
        self.attrs=dict()
        self.attrs_type=dict()
        if not os.path.exists(self.filename):
            # create a new TDM(s) file
#int DDC_CreateFile (const char *filePath, const char *fileType, const char *name, const char *description, const char *title, const char *author, DDCFileHandle *file);
            ddc_ck(NI.DDC_CreateFile (ufilename, self.fileType,  self.name,  self.description,  
                                      self.title,  self.author,  CT.byref(self.filehandle)))
        else:
            # open for read and write
            # int DDC_OpenFileEx (const char *filePath, const char *fileType, int readOnly, DDCFileHandle *file);
            ddc_ck(NI.DDC_OpenFileEx(ufilename, self.fileType,  self.readonly,  CT.byref(self.filehandle)))
        
        self.attrs=Attrs(DDC_File,  self.filehandle)
        self.get_Groups()
        
    def get_Groups(self):
        # ---- Groups
        #int DDC_GetNumChannelGroups (DDCFileHandle file, unsigned int *numberOfChannelGroups);
        noCG = CT.c_uint(0)
        ddc_ck(NI.DDC_GetNumChannelGroups (self.filehandle, CT.byref(noCG)))
        if noCG.value:
#            Grouphandles=(CT.c_int*noCG.value)()
            Grouphandles=(CT.POINTER(CT.c_int)*noCG.value)()

            ddc_ck(NI.DDC_GetChannelGroups (self.filehandle, CT.byref(Grouphandles),  noCG))
            
            for ghandle in Grouphandles:
                Group=TDM_Group(ghandle)
                self.Groups[Group.name]=Group
    
    def save(self):
        ddc_ck(NI.DDC_SaveFile (self.filehandle))

    def close(self):
        ddc_ck(NI.DDC_CloseFile (self.filehandle))
            
    def __contains__(self,  item):
        return item in self.Groups
    
    def __len__(self):
        return len(self.Groups)
        
    def __iter__(self):
        return self.Groups.__iter__()
            
    def __getitem__(self,  item):
        if item in self.Groups:
            return self.Groups[item]
        raise KeyError("%s is no Channelgroup"%(item))
    
    def __delitem__(self,  item):
        """
        delete a group in the TDMS file and the corresponding entry in the self.Channels dictionary
        and the TDM_Channel object
        """
        if item in self.Groups:
            group=self.Groups[item]
            ddc_ck(NI.DDC_RemoveChannelGroup (group.ghandle))
            for channelname in group:
                channel=group[channelname]
                del channel # delete the Python object TDM_Channel
                pass
            del self.Groups[item]  # remove the entry from the dictionary
        else:
            raise KeyError("Channelgroup %s not in TDM File"%(item))
                
    def add_Group(self, name,  description):
        if name not in self:
            ghandle=CT.c_int()
            ddc_ck(NI.DDC_AddChannelGroup(self.filehandle,  name,  description,  CT.byref(ghandle)))
            Group=TDM_Group(ghandle)
            self.Groups[Group.name]=Group
            return Group
        else:
            return self[name]


class TDM_Group(object):
    def __init__(self,  ghandle):
        self.ghandle=ghandle
        self.name=""
        self.Channels=dict()
        self.attrs=Attrs(DDC_Group,  ghandle)
        self.name=self.attrs["name"]
        self.get_Channels()
    
    def get_Channels(self):
        noCh=CT.c_uint(0)
        #int DDC_GetNumChannels (DDCChannelGroupHandle channelGroup, unsigned int *numberOfChannels);
        ddc_ck(NI.DDC_GetNumChannels(self.ghandle,  CT.byref(noCh)))
        if noCh.value:
#            channelhandles=(CT.c_int*noCh.value)()
            channelhandles=(CT.POINTER(CT.c_int)*noCh.value)()
            #int DDC_GetChannels (DDCChannelGroupHandle channelGroup, DDCChannelHandle channelsBuffer[], size_t numberOfChannels);
            ddc_ck(NI.DDC_GetChannels(self.ghandle,  channelhandles, noCh))
            for chandle in channelhandles:
                Channel=TDM_Channel(chandle)
                self.Channels[Channel.name]=Channel
    
    def __contains__(self,  item):
        return item in self.Channels
    
    def __len__(self):
        return len(self.Channels)
        
    def __iter__(self):
        return self.Channels.__iter__()
            
    def __getitem__(self,  item):
        if item in self.Channels:
            return self.Channels[item]
        raise KeyError("%s is no Channelgroup"%(item))
    
    # delete a channel
    def __delitem__(self,  item):
        if item in self.Channels:
            channel=self.Channels[item]
            ddc_ck(NI.DDC_RemoveChannel (channel.chandle))
            del self.Channels[item]
        else:
            raise KeyError("%s is no Channel in Channelgroup %s"%(item,  self.name))

    def add_Channel(self,  dataType,  name,  description="",  unitString=""):
#int DDC_AddChannel (DDCChannelGroupHandle channelGroup, DDCDataType dataType, 
#                     const char *name, const char *description, const char *unitString, DDCChannelHandle *channel);
        if name not in self.Channels:
            chandle=CT.c_int()
            ddc_ck(NI.DDC_AddChannel (self.ghandle,  dataType,  name,  description,  unitString,  CT.byref(chandle)))
            Channel=TDM_Channel(chandle)
            self.Channels[Channel.name]=Channel
            return Channel
        else:
            return self.Channels[name]


class TDM_Channel(object):
    def __init__(self,  chandle):
        self.chandle=chandle
        self.dataType=0
#        self.data=[]
        self.attrs=Attrs(DDC_Channel,  chandle)
        self.name=self.attrs["name"]
        
        dataType=CT.c_int()
        ddc_ck(NI.DDC_GetDataType(self.chandle,  CT.byref(dataType)))
        self.dataType=dataType.value
        noV=CT.c_uint64()
        ddc_ck(NI.DDC_GetNumDataValues(self.chandle,  CT.byref(noV)))
        self.noV=noV.value
        
    def __len__(self):
        noV=CT.c_uint64()
        ddc_ck(NI.DDC_GetNumDataValues(self.chandle,  CT.byref(noV)))
        self.noV=noV.value
        return self.noV
        
    def __getitem__(self,  index):
        """  get the data of the channel
        
             channel = channelhandle, returned by NI.DDC_GetChannels 
             Returns a Numpy array
             Timestamp data from TDM or TDMS are returned as a list of datetime.datetime objects
        """
        start,  stop,  step=self.check_index_get(index)
        noValues=stop-start
        if stop>self.noV:
            raise IndexError("tried to get more data from Channel % than available"%(self.name))
            
        data=[]    
        # TDMS has channels with zero length !!
        if noValues>0:
            if self.dataType in [DDC_UInt8,  DDC_Int16,  DDC_Int32, DDC_Double,  DDC_Float]:
                nptype=NP.dtype(Numpy_Types[self.dataType])
                data=NP.zeros(noValues,  nptype)
                contdata=NP.ascontiguousarray(data)
                cdatap=contdata.ctypes.data_as(CT.c_void_p)
                #    int DDC_GetDataValues (DDCChannelHandle channel, size_t indexOfFirstValueToGet, size_t numberOfValuesToGet, void *values);
                ddc_ck(NI.DDC_GetDataValues(self.chandle,  start,  noValues, cdatap ))
            elif self.dataType == DDC_String:
                str_arr=(CT.c_char_p*noValues)()
                ddc_ck(NI.DDC_GetDataValues(self.chandle,  start,  noValues, str_arr ))
                for i in range(0,  noValues):
#                    str=string_at(str_arr[i])
                    data.append(str_arr[i])
                    NI.DDC_FreeMemory(str_arr[i])
            elif self.dataType == DDC_Timestamp:
                years=(CT.c_uint*noValues)()
                months=(CT.c_uint*noValues)()
                days=(CT.c_uint*noValues)()
                hours=(CT.c_uint*noValues)()
                minutes=(CT.c_uint*noValues)()
                seconds=(CT.c_uint*noValues)()
                milliseconds=(CT.c_double*noValues)()
                weekdays=(CT.c_uint*noValues)()
                
                ddc_ck(NI.DDC_GetDataValuesTimestampComponents(self.chandle,  start,  noValues, 
                            years,  months,  days,  hours, minutes,  seconds,  milliseconds,  weekdays))
                
#                data=NP.zeros(noValues,  dtype=NP.dtype("float64"))
                data=[]
                for i in range(0,  noValues):
                    year=max(years[i],  1)  # must be greater than 0
                    month=min(max(months[i],  1),  12)
                    day=min(max(days[i],  1),  31)
                    dt=datetime.datetime(year,  month,  day,  
                            hours[i],  minutes[i],  seconds[i],  int(milliseconds[i]*1000))
                
                    data.append(dt)

        return data
    
    def __setitem__(self,  index,  values):
        # values must to be either numpy.ndarray or list
        if  isinstance(values,  list) or isinstance(values,  NP.ndarray):
            start,  stop,  step=self.check_index_set(index,  values)
            
            if not self.noV and start==0:
                # SetData
                self.set(values)
                return
                
            if start<self.noV-1:
                # ReplaceData
                self.replace(start,   values)
                return
                
        else:   #values is a not an array
            raise ValueError
        
    
    def set(self,   values):
        # convert to proper datatype
        ctype=DDC_ctypes[self.dataType]
        noV=len(values)
        
        # Timestamps should be a list of datetime.datetime objects
        if self.dataType== DDC_Timestamp:
            # values should be an array of datetime values
            if type(values[0]) != datetime.datetime:
                raise ValueError()
            #create single arrays of each component of datetime
            year=(CT.c_uint*noV)()
            month=(CT.c_uint*noV)()
            day=(CT.c_uint*noV)()
            hour=(CT.c_uint*noV)()
            minute=(CT.c_uint*noV)()
            second=(CT.c_uint*noV)()
            millisecond=(CT.c_double*noV)()
            
            for i in range(noV):
                dt=values[i]
                year[i]=dt.year
                month[i]=dt.month
                day[i]=dt.day
                hour[i]=dt.hour
                minute[i]=dt.minute
                second[i]=dt.second
                millisecond[i]=ms=float(dt.microsecond/1000)
            # int DDC_SetDataValuesTimestampComponents (DDCChannelHandle channel, unsigned int year[], unsigned int month[], unsigned int day[], unsigned int hour[], unsigned int minute[], unsigned int second[], double milliSecond[], size_t numValues);
            ddc_ck(NI.DDC_SetDataValuesTimestampComponents(self.chandle,  year,  month,  day, 
                                                hour,  minute,  second,  millisecond,  noV))
            self.noV=noV
            return
            
        # String arrays should be a list of strings
        if self.dataType== DDC_String:
            # create a character pointer array and set the pointers to the strings
# Todo
            array=(CT.c_char_p*noV)()
            if not isinstance(values[0],  basestring):
                raise ValueError()
            for i in range(noV):
#                array[i]=CT.create_string_buffer(values[i])
                array[i]=values[i]
            # NI.DDC_SetDataValuesString
            ddc_ck(NI.DDC_SetDataValuesString(self.chandle,  array,  noV))
            self.noV=noV
            return


        # all numerical values should be numpy arrays
        if type(values)==NP.ndarray or isinstance(values,  list):
            nptype=NP.dtype(Numpy_Types[self.dataType])
            contdata=NP.ascontiguousarray(values,  dtype=nptype)
            cdatap=contdata.ctypes.data_as(CT.c_void_p)
            #        int DDC_SetDataValues (DDCChannelHandle channel, void *values, size_t numberOfValues);
            ddc_ck(NI.DDC_SetDataValues(self.chandle,  cdatap,  noV))  
            self.noV=noV


        else:
            # the type of values is either a numpy.ndarray, nor Strings or datetime.datetime
            raise ValueError()
  
    def replace(self,  start ,   values):
        # convert to proper datatype
        ctype=DDC_ctypes[self.dataType]
        noV=len(values)
        
        # Timestamps should be a list of datetime.datetime objects
        if self.dataType== DDC_Timestamp:
            # values should be an array of datetime values
            if type(values[0]) != datetime.datetime:
                raise ValueError()
            #create single arrays of each component of datetime
            year=(CT.c_uint*noV)()
            month=(CT.c_uint*noV)()
            day=(CT.c_uint*noV)()
            hour=(CT.c_uint*noV)()
            minute=(CT.c_uint*noV)()
            second=(CT.c_uint*noV)()
            millisecond=(CT.c_double*noV)()
            
            for i in range(noV):
                dt=values[i]
                year[i]=dt.year
                month[i]=dt.month
                day[i]=dt.day
                hour[i]=dt.hour
                minute[i]=dt.minute
                second[i]=dt.second
                millisecond[i]=ms=float(dt.microsecond/1000)
 #           int DDC_ReplaceDataValuesTimestampComponents (DDCChannelHandle channel, 
#                                            unsigned int indexOfFirstValueToReplace, unsigned int year[], 
#                                            unsigned int month[], unsigned int day[], unsigned int hour[], unsigned int minute[], 
#                                            unsigned int second[], double milliSecond[], size_t numValues);
            ddc_ck(NI.DDC_ReplaceDataValuesTimestampComponents(self.chandle,  start,  year,  month,  day, 
                                    hour,  minute,  second,  millisecond,  noV))
            return
            
        # String arrays should be a list of strings
        if self.dataType== DDC_String:
            # create a character pointer array and set the pointers to the strings
# Todo
            array=(CT.c_char_p*noV)()
            if not isinstance(values[0],  basestring):
                raise ValueError()
            for i in range(noV):
                array[i]=values[i]
#            int DDC_ReplaceDataValuesString (DDCChannelHandle channel, size_t indexOfFirstValueToReplace, 
#                                             const char *values[], size_t numValues);
            ddc_ck(NI.DDC_ReplaceDataValuesString(self.chandle, start,  array,  noV))
            return

        # all numerical values should be numpy arrays
        if type(values)==NP.ndarray or isinstance(values,  list):
            nptype=NP.dtype(Numpy_Types[self.dataType])
            contdata=NP.ascontiguousarray(values,  dtype=nptype)
            cdatap=contdata.ctypes.data_as(CT.c_void_p)
            ddc_ck(NI.DDC_ReplaceDataValues(self.chandle,  start,  cdatap,  noV))
        else:
            # the type of values is either a numpy.ndarray, nor Strings or datetime.datetime
            raise ValueError()


    def append(self,  values):
        # convert to proper datatype
        ctype=DDC_ctypes[self.dataType]
        noV=len(values)
        
        # Timestamps should be a list of datetime.datetime objects
        if self.dataType== DDC_Timestamp:
            # values should be an array of datetime values
            if type(values[0]) != datetime.datetime:
                raise ValueError()
            #create single arrays of each component of datetime
            year=(CT.c_uint*noV)()
            month=(CT.c_uint*noV)()
            day=(CT.c_uint*noV)()
            hour=(CT.c_uint*noV)()
            minute=(CT.c_uint*noV)()
            second=(CT.c_uint*noV)()
            millisecond=(CT.c_double*noV)()
            
            for i in range(noV):
                dt=values[i]
                year[i]=dt.year
                month[i]=dt.month
                day[i]=dt.day
                hour[i]=dt.hour
                minute[i]=dt.minute
                second[i]=dt.second
                millisecond[i]=ms=float(dt.microsecond/1000)
            # int DDC_SetDataValuesTimestampComponents (DDCChannelHandle channel, unsigned int year[], unsigned int month[], unsigned int day[], unsigned int hour[], unsigned int minute[], unsigned int second[], double milliSecond[], size_t numValues);
            ddc_ck(NI.DDC_AppendDataValuesTimestampComponents(self.chandle,  year,  month,  day, 
                                                hour,  minute,  second,  millisecond,  noV))
            self.noV+=noV
            return
            
        # String arrays should be a list of strings
        if self.dataType== DDC_String:
            # create a character pointer array and set the pointers to the strings
# Todo
            array=(CT.c_char_p*noV)()
            if not isinstance(values[0],  basestring):
                raise ValueError()
            for i in range(noV):
                array[i]=values[i]
            # NI.DDC_SetDataValuesString
            ddc_ck(NI.DDC_AppendDataValuesString(self.chandle,  array,  noV))
            self.noV+=noV
            return

        # all numerical values should be numpy arrays
        if type(values)==NP.ndarray or isinstance(values,  list):
            nptype=NP.dtype(Numpy_Types[self.dataType])
            contdata=NP.ascontiguousarray(values,  dtype=nptype)
            cdatap=contdata.ctypes.data_as(CT.c_void_p)
            ddc_ck(NI.DDC_AppendDataValues(self.chandle,  cdatap,  noV))
            self.noV+=noV

        else:
            # the type of values is either a numpy.ndarray, nor Strings or datetime.datetime
            raise ValueError()
  


    def __iter__(self):
        for index in range(0,  self.noV):
            yield index
        

    def check_index_get(self,  index):
        t=type(index)
        if type(index) == int:
            start=index
            stop=index+1
            step=1

        elif type(index)==slice:
            start=index.start
            if not start:
                start=0
            stop=index.stop
            if not stop:
                stop=self.noV
            step=index.step
            if not step:
                step=1
            
        if start<0:
            start=self.noV+start
            
        if stop<0:
            stop=self.noV+stop
            
        
        if stop!= 0 and (start<0 or start>self.noV-1):
            raise IndexError("wrong index")
            pass
            
        return start,  stop,  step
            
    def check_index_set(self,  index,  values):
        t=type(index)
        max_i=max(self.noV,  len(values))
        if type(index) == int:
            start=index
            stop=index+1
            step=1
        
        elif type(index)==slice:
            start=index.start
            if not start:
                start=0
            stop=index.stop
            if not stop:
                stop=max_i
            step=index.step
            if not step:
                step=1
            
        if start<0:
            start=max_i+start
        
#        if stop>len(values):
#            stop=len(values)
            
        if stop<0:
            stop=max_i+stop
        
        if start<0:
            raise IndexError("wrong index")
            pass
            
        return start,  stop,  step
            

def ddc_ck(ret):
    """  raise an exception with a verbose error message
    """
    # -6214 : The property passed to the library does not have a value.
    if ret <0 and ret != -6214:
        msg=CT.string_at(NI.DDC_GetLibraryErrorDescription(ret) )
        print  ret,  msg
        raise BaseException(msg)
    return ret
        
class Timestamp(CT.Structure):
    def __init__(self):
        self.year=CT.c_uint(1)
        self.month=CT.c_uint(1) 
        self.day=CT.c_uint(1) 
        self.hour=CT.c_uint()
        self.minute=CT.c_uint() 
        self.second=CT.c_uint()
        self.millisecond=CT.c_double()
        self.weekday=CT.c_uint()
   
    def set_value(self):
        if self.year.value==0:
            self.year=CT.c_uint(1)
        if self.month.value==0:
            self.month=CT.c_uint(1)
        if self.day.value==0:
            self.day=CT.c_uint(1)
        dt=datetime.datetime(self.year.value,  self.month.value,  self.day.value,  
                    self.hour.value,  self.minute.value,  self.second.value,  int(self.millisecond.value*1000))
        self.value=dt

