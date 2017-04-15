# gpx-crawler
a gpx format running/riding crawler from Chinese sports website

此工具是一个用于获取网站上同步的GPS数据并且进行过滤，然后使用GPS Visualization Tools绘制运动轨迹。
GPS Visualization Tools可以从http://avtanski.net/projects/gps 获取，包括源码脚本。

此项目fork自ferventdesert/gpx-crawler，在此基础上完善了gps数据的获取与过滤。

这是原作者一年多的跑步记录绘制的全图：
![image](https://github.com/ferventdesert/gpx-crawler/blob/master/img/final2.png)

##1.数据来源

数据来源于益动GPS，可以导入其他数据源，如咕咚，Garmin手表，悦跑圈的数据。


##2.获取网站数据

1）获取用户ID(uid)

登录益动之后，点击一下头像，可以看到自己的uid，"user/"跟的数字即是。
http://edooon.com/user/******

2）获取cookies

将获取的cookies赋值给COOKIE变量，用于抓取数据时自动登录。如果当前脚本中的cookies与当前登录使用的不一致，获取数据将会失败。
Cookies的获取因浏览器的不同而有所不同，下面以傲游浏览器为例说明。

成功登录http://edooon.com 之后，打开"工具-开发者工具-Resources-Cookies"，可以看到所使用的cookies。
对于傲游浏览器来说，cookies是一些键值对，将所有的键值对使用";"进行连接，每个键值对使用"="进行赋值。如：

COOKIE='APP=25;APP=*;AuthCode=*;Hm_lpvt_c3e90e436c9afc3bedcb67690be7849d=*;Hm_lvt_c3e90e436c9afc3bedcb67690be7849d=*;JSESSIONID=*;originalApp=*'

3）获取数据

设置完成USERID和COOKIE之后，设置数据存储的本地路径LOCAL_PATH，之后运行脚本即可下载网站存储的GPS数据到本地，并自动转换为GPX格式。
上述获取数据使用脚本gpxCrawler.py。

##3.过滤GPX数据

因GPS Visualization Tools对于集中某个范围的数据展示效果较好，如果数据过于分散，则可能使得绘制部分轨迹无法绘制的问题。所以需要使用经纬度对范围进行一个过滤，确保数据不会出现较大的分散度。

过滤数据使用脚本gpxFiler.py。

需要指定过滤数据源LOCAL_PATH（即gpxCrawler.py中的存放数据的路径LOCAL_PATH）和过滤后数据存放路径LOCAL_PATH。
同时会在过滤数据源路径LOCAL_PATH中生成一个gpx.csv统计表。


##4.绘制GPX运动轨迹

运动轨迹的绘制参考http://avtanski.net/projects/gps 和原作者的博客http://python.jobbole.com/85808中的相关说明。

