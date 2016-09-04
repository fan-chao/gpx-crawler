#! C:\Python27
# -*- coding: utf-8 -*-

import sys   
import os
import shutil
import gpxpy
import gpxpy.parser as parser
import pandas as pd

LOCAL_PATH = u'F:\python\gpx\dataset\\'  #folder
DST_PATH = u'F:\python\gpx\gps_scripts\sample_gpx\\' #move filter files to this path 

class CityRange:
    def __init__(self, min_latitude, max_latitude, min_longitude, max_longitude):
        self._min_latitude_ = min_latitude
        self._max_latitude_ = max_latitude  
        self._min_longitude_ = min_longitude  
        self._max_longitude_ = max_longitude     

class GPXFilter:
    def __init__(self, path):
        self._path_ = path
        
    def extractSpecificCityData(self, city_range):
        data_frame = self.getRecordDataFrame()
        if len(data_frame) == 0:
            print "Data frame is Null."
            return data_frame
        
        city_data_frame = self.filterCity(data_frame, city_range)
        
        city_ids = city_data_frame['id']
            
        dst_path = DST_PATH
        if not os.path.exists(os.path.dirname(dst_path)):
            os.makedirs(os.path.dirname(dst_path))        
        self.moveFiles(city_ids, dst_path)
        
        print "All finished!"
        return city_data_frame
        
    def filterCity(self, data_frame, city_range):
        city_data_frame = data_frame.loc[(data_frame["lat"] > city_range._min_latitude_) & (data_frame["lat"] < city_range._max_latitude_) \
                     & (data_frame["lng"] > city_range._min_longitude_) & (data_frame["lng"] < city_range._max_longitude_)]
        return city_data_frame
        
    def  getRecordDataFrame(self):
        data_dic_list = []
        
        file_list = self.readFiles(self._path_)
        for file in file_list:
            data_dic = self.readGpx(file)
            if data_dic != None:
                data_dic_list.append(data_dic)    
        data_frame = pd.DataFrame(data_dic_list)
        return data_frame       
        
    def readGpx(self, file_name):
        gpx_file =  open(LOCAL_PATH + file_name + '.gpx', 'r')
        
        gpx_parser = parser.GPXParser(gpx_file)
        gpx = gpx_parser.parse()   
        gpx_file.close()            

        mvData = gpx.get_moving_data()
        dat = {'移动时间':mvData.moving_time, '静止时间':mvData.stopped_time, \
              '移动距离':mvData.moving_distance, '暂停距离':mvData.stopped_distance, \
              '最大速度':mvData.max_speed}
        dat['总时间'] = (gpx.get_duration())
        dat['id'] = file_name
        updown = gpx.get_uphill_downhill()
        dat['上山'] = (updown.uphill);
        dat['下山'] = (updown.downhill)
        timebound = gpx.get_time_bounds();
        dat['开始时间'] = (timebound.start_time)
        dat['结束时间'] = (timebound.end_time)
        p = gpx.get_points_data()[0]
        dat['lat'] = p.point.latitude
        dat['lng'] = p.point.longitude
        return dat  
    
    def readFiles(self, path):
        file_list =  []
        dir_list = os.listdir(path)
        for name in dir_list:
            if os.path.isfile(self._path_ + name):
                split_str = name.split('.')
                if split_str[1] != 'gpx':
                    continue              
                file_list.append(split_str[0])
        return file_list
    
    def moveFiles(self, ids, dst_path):
        for id in ids:
            file_name = id + '.gpx'
            file_path = os.path.join(LOCAL_PATH, file_name)
            if os.path.exists(file_path):
                shutil.move(file_path, os.path.join(DST_PATH, file_name))
           
if __name__ == '__main__':
    city_range = CityRange(34.16666667, 38.66666667, 114.33333333, 123.66666667) #山东省经纬度范围
    
    try:
        gpx_filter = GPXFilter(LOCAL_PATH)
        data_frame_sd = gpx_filter.extractSpecificCityData(city_range)
        
        if len(data_frame_sd) > 0:
           os.chdir(LOCAL_PATH)
           csv_file_name = 'gpx_sd.csv'
           if os.access(csv_file_name, os.W_OK):
               data_frame_sd.to_csv(csv_file_name, encoding="gb2312")
    except Exception, e:
         print e

     
