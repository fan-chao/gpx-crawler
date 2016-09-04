#! C:\Python27
# -*- coding: utf-8 -*-

import sys   
import time
import codecs;
import urllib2
import  re;
import json;
from lxml import etree

USERID='';  #enter your uid here
COOKIE='';  #folder

#Get html mode: 0-internet, 1-local file
GETHTMLMODE = 0


class GPXCrawler:
    def __init__(self, user_id, cookie, path):
        self._user_id_ = user_id
        self._cookie_ = cookie
        self._path_  = path
        self._opener_ = urllib2.build_opener()
        self._opener_.addheaders.append(('Cookie', self._cookie_))
        
    def crawlerData(self):
        allRecordList = self.getAllRecordList()
        self.extractRecordData(allRecordList)       
        
    def extractRecordData(self, record_list):
        export_path = '//*[@class="MD-feed-toolRight flex-auto"]/a';
        index = 1
        for record in record_list:
            print index
            print 'Record ID:' + record['recordID'] + '  ' + record['dateTime']  + '  ' + record['sportType']
            print str(record['distance']) + record['distanceUnit'] + '  ' \
            + str(record['timed']) + record['timedUnit'] + '  ' \
            + str(record['calories']) + record['caloriesUnit'] + '  ' \
            + str(record['averagePace']) + record['averagePaceUnit']
            index = index + 1
            
            record_id = record['recordID']
          
            record_url = 'http://edooon.com/user/%s/record/%s' % (self._user_id_, record_id)
            f = self._opener_.open(record_url)
            html = f.read()
            f.close()
   
            tree = self.getTree(html)
            idownload_str = str(tree.xpath(export_path)[0].attrib['href'])
            if idownload_str is None:
                continue
            
            download_url = 'http://edooon.com%s' %  idownload_str
            f = self._opener_.open(download_url);
            html = bytes.decode(f.read());
            html = html.replace('</trkpt>','</trkpt>\n').replace('</time>','</time>\n').replace('<time>','\n<time>')
            f.close();
            
            file_name = self._path_ + record_id + '.gpx';
            print file_name
            xmlfile = codecs.open(file_name, 'w');
            xmlfile.write(html);
            xmlfile.close();  
            
            print
    
    def getAllRecordList(self):
        '''
                Get all record list from all pages.
                Search all pages until none page record list is found.
                Each record contains record datetime, record id, sport type, sport distance, sport duration, 
                calories, average pace.
                Record id is most import element, which indicats the destinational page including data.
        '''        
        all_record_list = []
        
        if GETHTMLMODE == 0:
            page_num = 1
            while True:
                page_entry_html = self.crawHtml(page_num)
                page_tree = self.getTree(page_entry_html)
                page_record_list = self.getPageRecordList(page_tree)
                if len(page_record_list) == 0:
                    break
             
                all_record_list.extend(page_record_list)    
                page_num = page_num + 1        
        elif GETHTMLMODE == 1:
            page_entry_html = self.crawHtml(0)
            page_tree = self.getTree(page_entry_html)
            page_record_list = self.getPageRecordList(page_tree)
            if len(page_record_list) == 0:
                return all_record_list
         
            all_record_list.extend(page_record_list)                
            
        return all_record_list
        
    def crawHtml(self, page_num):
        entry_html = ""
        if GETHTMLMODE == 0:
            entry_url = "http://edooon.com/user/%s/record?pageNum=%d" % (self._user_id_, page_num)
            f = self._opener_.open(entry_url)     
            entry_html = f.read()        
            f.close()
        elif GETHTMLMODE == 1:
            f = codecs.open(self._path_ + 'record.htm', 'r', 'utf-8');
            entry_html = f.read();
            f.close();            
        return entry_html
    
    def getTree(self, html):
        root = etree.HTML(html)
        tree = etree.ElementTree(root)
        return tree
    
    def getPageRecordList(self, pageTree):
        page_record_list = []
        
        record_list_moder = pageTree.xpath('//*[@class="MD-recording-main-RecordList-moder"]')
        if len(record_list_moder) == 0:
            return page_record_list

        list_node = record_list_moder[0].xpath('div[@class="MD-recording-main-RecordList-redlist"]')
        if len(list_node)==0:
            return page_record_list
        
        page_record_node_list=list_node[0].xpath('div[@class="MD-recording-main-RecordList-li"]')    
        for record_node in page_record_node_list:
            record_dic = {}
            
            title_node_list = record_node.xpath('div[@class="MD-recording-main-RecordList-title"]')
            if len(title_node_list) == 0:
                continue
            
            #日期时间
            rec_datetime = title_node_list[0].xpath('span[1]/text()')[0]
            record_dic['dateTime'] = rec_datetime
            
            flex_box_node_list = record_node.xpath('div[@class="MD-recording-main-RecordList-run flexbox"]')
            if len(flex_box_node_list) == 0:
                continue   
            
            #record ID
            record_id = str(flex_box_node_list[0].attrib['onclick'])
            record_id = record_id.split('=')[-1].split('\'')[-2].split('/')[-1]
            record_dic['recordID'] = record_id
            
            #运动类型
            sport_type = flex_box_node_list[0].xpath('img[1]')[0].attrib['alt']
            record_dic['sportType'] = sport_type          
            
            #运动距离 - 单位：公里
            distance = float(flex_box_node_list[0].xpath('div[1]/span[1]/text()')[0])
            record_dic['distance'] = distance     
            
            distance_unit = flex_box_node_list[0].xpath('div[1]/span[2]/text()')[0]
            record_dic['distanceUnit'] = distance_unit                 
            
            #运动时间 - 单位：分钟
            timed = self.getTimeSeconds(flex_box_node_list[0].xpath('div[2]/span[1]/text()')[0])
            record_dic['timed'] = timed     
            
            record_dic['timedUnit'] = "秒".decode('utf-8')
            
            #消耗认证 - 单位：大卡
            calories = int(flex_box_node_list[0].xpath('div[3]/span[1]/text()')[0])
            record_dic['calories'] = calories     
            
            calories_unit = flex_box_node_list[0].xpath('div[3]/span[2]/text()')[0]
            record_dic['caloriesUnit'] = calories_unit      
            
            #平均配速 - 单位：m/km
            average_pace = 0
            pace_str = flex_box_node_list[0].xpath('div[4]/span[1]/text()')[0]
            if sport_type == "跑步".decode('utf-8'):
                average_pace = self.getTimeSeconds(pace_str)       
            elif sport_type == "步行".decode('utf-8'):
                average_pace = float(pace_str)
            record_dic['averagePace'] = average_pace     
            
            averag_pace_unit = flex_box_node_list[0].xpath('div[4]/span[2]/text()')[0]
            record_dic['averagePaceUnit'] = averag_pace_unit     
            
            page_record_list.append(record_dic)     
        
        return page_record_list  
    
    def getTimeSeconds(self, strtimed):
        temp_list = strtimed.split(':')
        if len(temp_list) == 0:
            return 0    
        elif len(temp_list) == 1:
            return int(temp_list[0]) 
        elif len(temp_list) == 2:
            return int(temp_list[0])*60 + int(temp_list[1])
        elif len(temp_list) == 3:
            return int(temp_list[0])*3600 + int(temp_list[1])*60 + + int(temp_list[2])
       

if __name__ == '__main__':
     gpxCrawler = GPXCrawler(USERID, COOKIE, LOCAL_PATH)
     gpxCrawler.crawlerData()
     print ('All finished!')

     
