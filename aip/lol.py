from datetime import datetime

t = '2020-01-30T17:00:00Z'
fmt = '%Y-%m-%dT%H:%M:%S%fZ'

dtt = datetime.strptime(t, fmt)

print type(dtt),dtt











# import datetime
# 
# epoch = datetime.datetime(1970,1,1)
# 
# t = '2020-01-30T17:00:00Z'
# 
# dt = datetime.datetime.strptime(t, '%Y-%m-%dT%H:%M:%S%fZ') 
# print dt
# 
# et = (dt - epoch).total_seconds()
# 
# print et
# 
# 
# # et = datetime.datetime(dt).strftime('%s')
# # print et
