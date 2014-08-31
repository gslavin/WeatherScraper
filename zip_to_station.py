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
        i = 1
        zip_regions = zip_regions[1:]
        for region_info in zip_regions:
            region_info = region_info.split(',')
            #remove Null strings
            region_info = list(filter(bool,region_info))
            if len(region_info) == 0:
                continue
            if len(region_info) != 5:
                print("Malformed sequence", i)
                print(region_info)
                continue
            state = region_info[0]
            city = region_info[1]
            zip_code = region_info[2]
            latitude = region_info[3]
            longitude = region_info[4]
            region = ZipRegion(state, city, zip_code, latitude, longitude)
            region_list.append(region)
            i = i+1
        print(i,"zip codes on file")
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
    print(len(weather_station_list), "weather stations found.")
    return weather_station_list
    
    
def get_station_file():
    station_index = "http://w1.weather.gov/xml/current_obs/index.xml"
    
    http_rsp_obj = urlr.urlopen(station_index)

    #reads as bytes
    weather_xml = http_rsp_obj.read()

    #turn weather_xml into a string from bytes
    weather_xml = weather_xml.decode(encoding='UTF-8')
    return weather_xml

# TODO update to a balanced tree
# TODO: restructure class to get rid of annoying checks for Nones
# TODO: should all attributes be kept as strings?  Even lat and long?
# Create a binary search tree from list of stations 
class binary_tree:
    def __init__(self, station, sort_field):
        self.data = station
        self.sort_field = sort_field
        self.left = None
        self.right = None

    def insert(self, station):
        # place node right if greater
        if float(station.station_info[self.sort_field]) > \
         float(self.data.station_info[self.sort_field]):
            if self.right == None:
                self.right = binary_tree(station, self.sort_field)
            else:
                self.right.insert(station)
        #place node left if less
        else:
            if self.left == None:
                self.left = binary_tree(station, self.sort_field)
            else:
                self.left.insert(station)
    def size(self):
        if self.left == None:
            left_size = 0
        else:
            left_size = self.left.size()
        if self.right == None:
            right_size = 0
        else:
            right_size = self.right.size()
        return 1 + left_size + right_size
    # Searches the tree for stations within a specified distance
    # returns a list of stations that are within the specified distance
    def find_station(self, value, distance):
        if float(self.data.station_info[self.sort_field]) < (value - distance):
            if self.right is not None:
                return self.right.find_station(value, distance)
            else:
                return []
        elif float(self.data.station_info[self.sort_field]) > (value + distance):
            if self.left is not None:
                return self.left.find_station(value, distance)
            else:
                return []
        else:
            right_values = []
            left_values = []
            if self.right is not None:
                right_values = self.right.find_station(value, distance) 
            if self.left is not None:
                left_values = self.left.find_station(value, distance)
            return [self.data] + right_values + left_values
            

# converts linear lists into binary serach trees
def station_list_to_tree(station_list, sort_field):
    station_tree = binary_tree(station_list[0], sort_field)
    for station in station_list[1:]:
        station_tree.insert(station)
    return station_tree

#Uses a binary search tree to locate close stations
def better_map_zip_to_station(region_list, weather_station_list):
    zip_to_station_map = {}
    # chane linear lists into binary search trees
    lat_station_tree = station_list_to_tree(weather_station_list, "latitude")
    long_station_tree = station_list_to_tree(weather_station_list, "longitude")
    print("lat map size:", lat_station_tree.size())
    print("long map size:", long_station_tree.size())
    for region in region_list:
        # make a list of all stations within distance degrees
        distance = 0.1
        close_stations = []
        # check for stations in a widening circle
        while(close_stations == []):
            long_stations = long_station_tree.find_station(float(region.longitude), distance)
            lat_stations = lat_station_tree.find_station(float(region.latitude), distance)
            close_stations = list(set(lat_stations) & set(long_stations))
            distance = distance + 0.1
        # start with large initial distance
        shortest_distance = 1e20
        for close_station in close_stations:
            distance = (float(region.latitude) - float(close_station.station_info["latitude"]))**2 + \
                               (float(region.longitude)- float(close_station.station_info["longitude"]))**2
            if distance < shortest_distance:
                zip_to_station_map[region.zip_code] \
                    = close_station.station_info["xml_url"]
                shortest_distance = distance
    return zip_to_station_map
    
def map_zip_to_station(region_list, weather_station_list):
    zip_to_station_map = {}
    for region in region_list:
        shortest_distance = 1000000
        for station in weather_station_list:
            # Using distance squared because actual distance doesn't matter.
            # only what is closest
            distance = (float(region.latitude) - float(station.station_info["latitude"]))**2 + \
                               (float(region.longitude)- float(station.station_info["longitude"]))**2
            if distance < shortest_distance:
                zip_to_station_map[region.zip_code] \
                    = station.station_info["xml_url"]
                shortest_distance = distance
    return zip_to_station_map
    
def main():
    region_list = parse_zip_region_file("cityzip.csv")
    weather_station_list = parse_station_file(get_station_file())
    zip_to_station_map = better_map_zip_to_station(region_list, weather_station_list)
    with open("zip_to_station_map","wb") as f:
        pickle.dump(zip_to_station_map, f)
        
if __name__ == "__main__":
    main()
