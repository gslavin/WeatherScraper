import urllib.request as urlr
import datetime as dt
import pickle
import sys

def get_url(zip_code):
    with open("zip_to_station_map",'rb') as f:
        zip_to_station = pickle.load(f)
        return zip_to_station[zip_code]
    

def log_data(weather_xml):
    date = dt.date.today()
    with open("weather_%s.txt" % (date.isoformat()), "w") as f:
        f.write(weather_xml)
    
    
def parse_weather_xml(weather_xml, weatherReport):
    for line in weather_xml.split('\n'):
        for attribute in weatherReport.attributes:
            tag = '<' + attribute + '>'
            if tag in line:
                start_index = line.index('>') + 1
                end_index = line.index('<', start_index)
                weatherReport.weather_data[attribute] = line[start_index:end_index]
                
class WeatherReport():
    def __init__(self):
        self.attributes = ["location", "station_id","latitude", "longitude", \
                "observation_time", "weather", "temperature_string", \
                "wind_string", "pressure_string", "dewpoint_string", \
                "windchill_string", "visibility_mi","water_temp_f"]
        self.weather_data = {}
    
    def remove_unused_attributes(self):
        self.attributes = [attribute for attribute in self.attributes \
                            if attribute in self.weather_data]
    
    def to_string(self):
        output = ""
        for attribute in self.attributes:
            output += attribute.replace("_string","") + ": " \
                      + self.weather_data[attribute] + '\n'
        return output
            
#west chest weather http://www.wunderground.com/US/PA/West_Chester.html
#url = "http://forecast.weather.gov/MapClick.php?lat=39.95980&lon=-75.6061&unit=0&lg=english&FcstType=dwml"



#current weather at Phlly airport
PHILLY_ZIP = "19105"

def main(zip_code = PHILLY_ZIP):
    url = get_url(zip_code)
    http_rsp_obj = urlr.urlopen(url)

    #reads as bytes
    weather_xml = http_rsp_obj.read()

    #turn weather_xml into a string from bytes
    weather_xml = weather_xml.decode(encoding='UTF-8')

    weatherReport = WeatherReport()
    parse_weather_xml(weather_xml, weatherReport)

    weatherReport.remove_unused_attributes()

    print(weatherReport.to_string())

    log_data(weather_xml)

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Too many arguments")
        exit()
    elif len(sys.argv) == 2:
        try:
            int(sys.argv[1])
        except:
            print("using default location:",PHILLY_ZIP)
            main()
        if len(sys.argv[1]) != 5:
            print("Weather Data unavailable: invalid zip code")
            exit()
        main(sys.argv[1])
    else:
        main()
