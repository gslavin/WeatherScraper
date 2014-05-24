import math
import urllib.request as urlr
import pickle

class WeatherStation:
    def __init__(self):
        self.attributes = ["station_name", "latitude", "longitude", "xml_url"]
        self.station_info = {}
    
    def print_station_info(self):
        for attribute in self.attributes:
            print(attribute + ": ", self.station_info[attribute])
    
    def to_string(self):
        output = ""
        for attribute in self.attributes:
            output += attribute + ": " \
                      + self.station_info[attribute] + '\n'
        return output
class ZipRegion:
    def __init__(self, state, city, zip_code, latitude, longitude):
        self.state = state
        self.city = city
        self.zip_code = zip_code
        self.latitude = latitude
        self.longitude = longitude
    def print_info(self):
        print(self.state)
        print(self.city)
        print(self.zip_code)
        print(self.latitude)
        print(self.longitude)
        print()
def parse_zip_region_file(filename):
    region_list = []
    with open(filename,'r') as f:
        zip_regions = f.read().split('\n')
        #first line is header
        #State City Postal Latitude Longitude
        zip_regions = zip_regions[1:]
        for region_info in zip_regions:
            region_info = region_info.split(',')
            #remove Null strings
            region_info = list(filter(bool,region_info))
            if len(region_info) != 5:
                print("Malformed sequence")
                print(region_info)
                continue
            state = region_info[0]
            city = region_info[1]
            zip_code = region_info[2]
            latitude = region_info[3]
            longitude = region_info[4]
            region = ZipRegion(state, city, zip_code, latitude, longitude)
            region_list.append(region)
    return region_list
    
def parse_station_file(weather_xml):
    weather_station_list = []
    #last last after last station is just a footer 
    for station in weather_xml.split("</station>")[:-1]:
        weather_station = WeatherStation()
        station_info = station.split("<station>")[-1]
        station_info = station_info.split("\n")
        for line in station_info:
            for attribute in weather_station.attributes:
                if '<' + attribute + '>' in line:
                    start_index = line.index('>') + 1
                    end_index = line.index('<', start_index)
                    weather_station.station_info[attribute] \
                        = line[start_index:end_index]
        weather_station_list.append(weather_station)
    return weather_station_list
    
    
def get_station_file():
    station_index = "http://w1.weather.gov/xml/current_obs/index.xml"
    
    http_rsp_obj = urlr.urlopen(station_index)

    #reads as bytes
    weather_xml = http_rsp_obj.read()

    #turn weather_xml into a string from bytes
    weather_xml = weather_xml.decode(encoding='UTF-8')
    return weather_xml
    
    
def map_zip_to_station(region_list, weather_station_list):
    zip_to_station_map = {}
    #high distance to start off
    i = 0
    for region in region_list:
        shortest_distance = 1000000
        for station in weather_station_list:
            distance = math.sqrt((float(region.latitude) - float(station.station_info["latitude"]))**2 + \
                               (float(region.longitude)- float(station.station_info["longitude"]))**2)
            if distance < shortest_distance:
                zip_to_station_map[region.zip_code] \
                    = station.station_info["xml_url"]
                shortest_distance = distance
    return zip_to_station_map
    
def main():
    region_list = parse_zip_region_file("cityzip.csv")
    weather_station_list = parse_station_file(get_station_file())
    zip_to_station_map = map_zip_to_station(region_list, weather_station_list)
    with open("zip_to_station_map","wb") as f:
        pickle.dump(zip_to_station_map, f)
        
if __name__ == "__main__":
    print("running main")
    main()