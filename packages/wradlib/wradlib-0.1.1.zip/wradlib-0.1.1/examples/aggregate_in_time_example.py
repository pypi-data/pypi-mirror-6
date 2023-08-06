#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      heistermann
#
# Created:     15.11.2012
# Copyright:   (c) heistermann 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

def main():
    pass

if __name__ == '__main__':
    import datetime as dt
    dt_trg = from_to("2012-10-26 00:00:00", "2012-10-26 01:00:00", 3600)
    dt_src = ["2012-10-26 00:05:00", "2012-10-26 00:15:00", "2012-10-26 00:30:00", "2012-10-26 01:00:00"]
    dt_src = [dt.datetime.strptime(tstep, "%Y-%m-%d %H:%M:%S") for tstep in dt_src]
    src = np.array([[1,1,1,1],[2,2,2,2],[3,3,3,3], [4,4,4,4]])
    print average_over_time_windows(src, dt_src, dt_trg)
