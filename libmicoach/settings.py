# Global configuration


# 
email = ""
# 
password = ""
# 
timezoneinfo = "-300,true,BYDAY=2SU;BYMONTH=3,BYDAY=1SU;BYMONTH=11"

# 
trace = True # remplacer par logging very very verbose
debug = True
# 
authcookie = None
# 
isconnected = False

#
save_csv = True
save_xml = True

csv_path = "data/{username}/{date} - {name}.csv"
xml_path = "data/{username}/xml/{date} - {name}.xml"

csv_format = "{time}; {heart}; {calories}; {pace};"
