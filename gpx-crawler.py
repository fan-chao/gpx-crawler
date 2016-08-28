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
COOKIE=''  #enter your cookie here
LOCAL_PATH = u'';  #local path used to store data set

#Get html mode: 0-internet, 1-local file
GETHTMLMODE = 0


class GPXCrawler:
    def __init__(self, userID, cookie, path):
        self._userID_ = userID
        self._cookie_ = cookie
        self._path_  = path
        self._opener_ = urllib2.build_opener()
        self._opener_.addheaders.append(('Cookie', self._cookie_))
        
    def crawlerData(self):
        allRecordList = self.getAllRecordList()
        self.extractRecordData(allRecordList)       
        
    def extractRecordData(self, recordList):
        export_path = '//*[@class="MD-feed-toolRight flex-auto"]/a';
        index = 1
        for record in recordList:
            print index
            print 'Record ID:' + record['recordID'] + '  ' + record['dateTime']  + '  ' + record['sportType']
            print str(record['distance']) + record['distanceUnit'] + '  ' \
            + str(record['timed']) + record['timedUnit'] + '  ' \
            + str(record['calories']) + record['caloriesUnit'] + '  ' \
            + str(record['averagePace']) + record['averagePaceUnit']
            index = index + 1
            
            recordID = record['recordID']
          
            recordUrl = 'http://edooon.com/user/%s/record/%s' % (self._userID_, recordID)
            f = self._opener_.open(recordUrl)
            html = f.read()
            f.close()
   
            tree = self.getTree(html)
            idownloadStr = str(tree.xpath(export_path)[0].attrib['href'])
            if idownloadStr is None:
                continue
            
            downloadUrl = 'http://edooon.com%s' %  idownloadStr
            f = self._opener_.open(downloadUrl);
            html = bytes.decode(f.read());
            html = html.replace('</trkpt>','</trkpt>\n').replace('</time>','</time>\n').replace('<time>','\n<time>')
            f.close();
            
            filename = self._path_ + recordID + '.gpx';
            print filename
            xmlfile = codecs.open(filename, 'w');
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
        allRecordList = []
        
        if GETHTMLMODE == 0:
            pageNum = 1
            while True:
                pageEntryHtml = self.crawHtml(pageNum)
                pageTree = self.getTree(pageEntryHtml)
                pageRecordList = self.getPageRecordList(pageTree)
                if len(pageRecordList) == 0:
                    break
             
                allRecordList.extend(pageRecordList)    
                pageNum = pageNum + 1        
        elif GETHTMLMODE == 1:
            pageEntryHtml = self.crawHtml(0)
            pageTree = self.getTree(pageEntryHtml)
            pageRecordList = self.getPageRecordList(pageTree)
            if len(pageRecordList) == 0:
                return allRecordList
         
            allRecordList.extend(pageRecordList)                
            
        return allRecordList
        
    def crawHtml(self, pageNum):
        entryHtml = ""
        if GETHTMLMODE == 0:
            entryUrl = "http://edooon.com/user/%s/record?pageNum=%d" % (self._userID_, pageNum)
            f = self._opener_.open(entryUrl)     
            entryHtml = f.read()        
            f.close()
        elif GETHTMLMODE == 1:
            f = codecs.open(self._path_ + 'record.htm', 'r', 'utf-8');
            entryHtml = f.read();
            f.close();            
        return entryHtml
    
    def getTree(self, html):
        root = etree.HTML(html)
        tree = etree.ElementTree(root)
        return tree
    
    def getPageRecordList(self, pageTree):
        pageRecordList = []
        
        recordListModer = pageTree.xpath('//*[@class="MD-recording-main-RecordList-moder"]')
        if len(recordListModer) == 0:
            return pageRecordList

        listNode = recordListModer[0].xpath('div[@class="MD-recording-main-RecordList-redlist"]')
        if len(listNode)==0:
            return pageRecordList
        
        pageRecordNodeList=listNode[0].xpath('div[@class="MD-recording-main-RecordList-li"]')    
        for recordNode in pageRecordNodeList:
            recordDic = {}
            
            titleNodeList = recordNode.xpath('div[@class="MD-recording-main-RecordList-title"]')
            if len(titleNodeList) == 0:
                continue
            
            #日期时间
            recDatetime = titleNodeList[0].xpath('span[1]/text()')[0]
            recordDic['dateTime'] = recDatetime
            
            flexBoxNodeList = recordNode.xpath('div[@class="MD-recording-main-RecordList-run flexbox"]')
            if len(flexBoxNodeList) == 0:
                continue   
            
            #record ID
            recordID = str(flexBoxNodeList[0].attrib['onclick'])
            recordID = recordID.split('=')[-1].split('\'')[-2].split('/')[-1]
            recordDic['recordID'] = recordID
            
            #运动类型
            sportType = flexBoxNodeList[0].xpath('img[1]')[0].attrib['alt']
            recordDic['sportType'] = sportType          
            
            #运动距离 - 单位：公里
            distance = float(flexBoxNodeList[0].xpath('div[1]/span[1]/text()')[0])
            recordDic['distance'] = distance     
            
            distanceUnit = flexBoxNodeList[0].xpath('div[1]/span[2]/text()')[0]
            recordDic['distanceUnit'] = distanceUnit                 
            
            #运动时间 - 单位：分钟
            timed = self.getTimeSeconds(flexBoxNodeList[0].xpath('div[2]/span[1]/text()')[0])
            recordDic['timed'] = timed     
            
            recordDic['timedUnit'] = "秒".decode('utf-8')
            
            #消耗认证 - 单位：大卡
            calories = int(flexBoxNodeList[0].xpath('div[3]/span[1]/text()')[0])
            recordDic['calories'] = calories     
            
            caloriesUnit = flexBoxNodeList[0].xpath('div[3]/span[2]/text()')[0]
            recordDic['caloriesUnit'] = caloriesUnit      
            
            #平均配速 - 单位：m/km
            averagePace = 0
            paceStr = flexBoxNodeList[0].xpath('div[4]/span[1]/text()')[0]
            if sportType == "跑步".decode('utf-8'):
                averagePace = self.getTimeSeconds(paceStr)       
            elif sportType == "步行".decode('utf-8'):
                averagePace = float(paceStr)
            recordDic['averagePace'] = averagePace     
            
            averagePaceUnit = flexBoxNodeList[0].xpath('div[4]/span[2]/text()')[0]
            recordDic['averagePaceUnit'] = averagePaceUnit     
            
            pageRecordList.append(recordDic)     
        
        return pageRecordList  
    
    def getTimeSeconds(self, strtimed):
        tempList = strtimed.split(':')
        if len(tempList) == 0:
            return 0    
        elif len(tempList) == 1:
            return int(tempList[0]) 
        elif len(tempList) == 2:
            return int(tempList[0])*60 + int(tempList[1])
        elif len(tempList) == 3:
            return int(tempList[0])*3600 + int(tempList[1])*60 + + int(tempList[2])
       

if __name__ == '__main__':
     gpxCrawler = GPXCrawler(USERID, COOKIE, LOCAL_PATH)
     gpxCrawler.crawlerData()

     
