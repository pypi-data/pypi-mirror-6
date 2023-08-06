# /usr/bin/env python

# Uses data from DB-IP.com (http://db-ip.com/) database
import time
import MySQLdb 
import urllib 
import json 

oppiadb = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                      passwd="littleal", # your password
                      db="python") # name of the data base
oppiacur = oppiadb.cursor() 

ipdb = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                      passwd="littleal", # your password
                      db="ipdb") # name of the data base
ipdbcur = ipdb.cursor() 

# Use all the SQL you like
oppiacur.execute("SELECT ip , count(*) as count_hits FROM oppia_tracker GROUP BY ip")

print oppiacur.rowcount
# print all the first cell of all the rows
for row in oppiacur.fetchall() :
    # lookup whether already cached in db
    ipdbcur.execute("SELECT lat, lng FROM dbip_cache WHERE ip='" + row[0]+ "'")
    ver = ipdbcur.fetchone()
    if ipdbcur.rowcount == 0:
         # if not cached then call to Geonames db
        # and insert into cache
        url = 'http://api.ipaddresslabs.com/iplocation/v1.7/locateip?key=SAK939UX5LK65FVXY6ZZ&ip='+row[0]+'&format=json'
        #url = 'http://api.geonames.org/searchJSON?username=alexlittle&maxRows=1&q='+urllib.quote_plus(ipdbver[2])+'&country='+urllib.quote_plus(ipdbver[0])
        print row[0] + " : "+ url
        u = urllib.urlopen(url)
        data = u.read()  
        dataJSON = json.loads(data)
        print dataJSON
        if 'geolocation_data' in dataJSON:
            print dataJSON['geolocation_data']
            
            url = 'http://api.geonames.org/searchJSON?username=alexlittle&maxRows=1&q='+urllib.quote_plus(dataJSON['geolocation_data']['region_name'])+'&country='+urllib.quote_plus(dataJSON['geolocation_data']['country_code_iso3166alpha2'])
            u = urllib.urlopen(url)
            geo = u.read()  
            geoJSON = json.loads(geo)
            print geoJSON
            try:
                ipdbcur.execute("INSERT INTO dbip_cache (ip,lat,lng, hits, region, country) VALUES " +
                                "('"+ row[0]+"',"+str(geoJSON['geonames'][0]['lat'])+","+str(geoJSON['geonames'][0]['lng']) +
                                ","+str(row[1])+",%s,%s)",(geoJSON['geonames'][0]['name'],geoJSON['geonames'][0]['countryCode'],))
                ipdb.commit()
            except UnicodeEncodeError:
                pass
                
        time.sleep(3)
    else:
        #print "found in cache"
        ipdbcur.execute("UPDATE dbip_cache SET hits ="+str(row[1])+" WHERE ip='"+str(row[0])+"'")
        ipdb.commit()
        print "hits updated"
   
    #print row[0]
oppiacur.close()
ipdbcur.close()

oppiadb.close()
ipdb.close()

''' 
url = 'http://api.geonames.org/searchJSON?username=alexlittle&maxRows=1&q=winchester&country=GB'
u = urllib.urlopen(url)
# u is a file-like object
data = u.read()  
dataJSON = json.loads(data)
#print dataJSON
#print dataJSON['geonames']
print dataJSON['geonames'][0]['lat'] + ":" + dataJSON['geonames'][0]['lng'] 
'''    