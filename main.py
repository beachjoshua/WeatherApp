#python code for backend
import requests

class LocationData():
    def __init__(self):
        self.state = ""
        self.state_name = ""
        self.city = ""
        self.lat = 0
        self.lon = 0

    # gets user location based on their IP address
    def get_user_location(self):
        try:
            r = requests.get("http://ip-api.com/json/").json()
        except:
            raise Exception("Could not get user location")
            
        self.state = r["region"]
        self.state_name = r["regionName"]
        self.city = r["city"]
        self.lat = r["lat"]
        self.lon = r["lon"]
    
    def search_location(self):
        # to-do
        pass
    
    # returns a dictionary with location data
    def to_dict(self):
        return {
        "state": self.state,
        "state_name": self.state_name,
        "city": self.city,
        "lat": self.lat,
        "lon": self.lon
        }


class WeatherData():
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
        self.update_weather()
    
    # updates weather data
    def update_weather(self):
        r = requests.get(f"https://api.weather.gov/points/{self.lat},{self.lon}").json()
        
        forecast_endpoint = requests.get(r["properties"]["forecast"]).json()
        forecast_hourly_endpoint = requests.get(r["properties"]["forecastHourly"]).json()
        
        # gets the forecast for every 12hr period for the next 7 days
        self.forecast = forecast_endpoint["properties"]["periods"]
        # gets the forecast for every hour for the next 7 days
        self.forecast_hourly = forecast_hourly_endpoint["properties"]["periods"]


def main() -> None:
    # example usage
    
    l = LocationData()
    l.get_user_location()
    w = WeatherData(l.lat, l.lon)
    
    # prints city and state
    print(f"Weather data for {l.city}, {l.state}:\n")
    
    # prints the current temperature and weather
    print(f"Current Temperature: {w.forecast_hourly[0]['shortForecast']}\n")
    print(f"Current Weather: {w.forecast_hourly[0]['temperature']}°{w.forecast_hourly[0]['temperatureUnit']}\n")
    
    # prints the forecast for the current 12hr period
    print(f"Current 12hr Weather Forecast: {w.forecast[0]['detailedForecast']}\n")
    
    # prints the temperature and weather over the next 7 days
    print("7 day forecast:")
    for i in range(1, len(w.forecast)):
        print(f"{w.forecast[i]['name']}:")
        print(f"{w.forecast[i]['detailedForecast']}")
        
    
if __name__ == "__main__":
    main()


'''
Important URLs:
https://api.weather.gov/gridpoints/SGF/121,69/forecast
https://api.weather.gov/gridpoints/SGF/121,69/forecast/hourly
'''
