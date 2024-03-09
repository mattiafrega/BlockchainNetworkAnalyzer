from datetime import datetime, timedelta

def datetimeToUnixTs(startTime, endTime ):
    # Convert input date string to datetime object
    start_time = datetime.strptime(startTime,'%Y-%m-%dT%H:%M')
    end_time = datetime.strptime(endTime,'%Y-%m-%dT%H:%M')
    
    # Convert datetime objects to Unix timestamps
    start_unix_timestamp = start_time.timestamp()
    end_unix_timestamp = end_time.timestamp()
    
    print("start time: "+ str(start_unix_timestamp)+ " end time: "+ str(end_unix_timestamp))
    return int(start_unix_timestamp), int(end_unix_timestamp)
