from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import requests
import traceback

app = Flask(__name__)
CORS(app)

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
    
    # lets user search for locations manually
    def search_location(self, query):
        results = []

        osm_url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&addressdetails=1&countrycodes=us&limit=5"
        osm_response = requests.get(osm_url, headers={'User-Agent': 'WeatherApp/1.0'})

        if osm_response.status_code == 200:
            osm_data = osm_response.json()
                    
            for item in osm_data:
                city = item.get('address', {}).get('city', "")
                if not city:
                    city = item.get('address', {}).get('town', "")
                if not city:
                    city = item.get('address', {}).get('village', "")
                if not city and 'display_name' in item:
                    parts = item['display_name'].split(',')
                    if parts:
                        city = parts[0].strip()
                        
                state_name = item.get('address', {}).get('state', "")

                state_abbrv = {
                    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
                    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
                    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
                    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
                    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
                    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
                    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
                    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
                    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
                    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
                    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
                    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
                    "Wisconsin": "WI", "Wyoming": "WY"
                }

                state_code = state_abbrv.get(state_name)
                                           
                results.append({
                     "state": state_code,
                     "state_name": state_name,
                      "city": city,
                       "lat": float(item['lat']),
                      "lon": float(item['lon']),
                       "display_name": item['display_name'] # for frontend
                 })
            
            # make sure all results have required fields
            for result in results:
                if not result.get('city'):
                    result['city'] = "Unknown Location"
                if not result.get('state_name'):
                    result['state_name'] = ""
                if not result.get('state'):
                    result['state'] = ""
                        
        return results
    
    # sets location from search result
    def set_from_search_result(self, result):
        self.state = result.get('state', '')
        self.state_name = result.get('state_name', '')
        self.city = result.get('city', '')
        self.lat = result.get('lat', 0)
        self.lon = result.get('lon', 0)
        return self
    
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
        self.forecast = []
        self.forecast_hourly = []
        self.update_weather()
    
    # updates weather data
    def update_weather(self):
        try:
            # Debug output
            print(f"Fetching weather for coordinates: {self.lat}, {self.lon}")
            
            # Get the grid point data
            points_url = f"https://api.weather.gov/points/{self.lat},{self.lon}"
            print(f"API URL: {points_url}")
            
            points_response = requests.get(points_url)
            
            if points_response.status_code != 200:
                print(f"Error from weather.gov API: {points_response.status_code}")
                print(points_response.text)
                raise Exception(f"Weather API returned error status: {points_response.status_code}")
            
            r = points_response.json()
            
            # Get forecast URLs
            forecast_url = r["properties"]["forecast"]
            forecast_hourly_url = r["properties"]["forecastHourly"]
            
            print(f"Forecast URL: {forecast_url}")
            print(f"Hourly Forecast URL: {forecast_hourly_url}")
            
            # Get forecast data
            forecast_response = requests.get(forecast_url)
            if forecast_response.status_code != 200:
                print(f"Error from forecast API: {forecast_response.status_code}")
                print(forecast_response.text)
                raise Exception(f"Forecast API returned error status: {forecast_response.status_code}")
                
            forecast_endpoint = forecast_response.json()
            
            # Get hourly forecast data
            forecast_hourly_response = requests.get(forecast_hourly_url)
            if forecast_hourly_response.status_code != 200:
                print(f"Error from hourly forecast API: {forecast_hourly_response.status_code}")
                print(forecast_hourly_response.text)
                raise Exception(f"Hourly forecast API returned error status: {forecast_hourly_response.status_code}")
                
            forecast_hourly_endpoint = forecast_hourly_response.json()
            
            # gets the forecast for every 12hr period for the next 7 days
            self.forecast = forecast_endpoint["properties"]["periods"]
            # gets the forecast for every hour for the next 7 days
            self.forecast_hourly = forecast_hourly_endpoint["properties"]["periods"]
            
        except Exception as e:
            print(f"Error updating weather: {e}")
            print(traceback.format_exc())  # Print detailed exception info
            # Don't set empty values - the to_dict method will handle the error
    
    # creates dictionary with data
    def to_dict(self):
        if not self.forecast_hourly or not self.forecast:
            return {
                "error": "Unable to retrieve weather data for this location. The location might be outside the coverage area of the National Weather Service API."
            }
            
        return {
            "current_temperature": self.forecast_hourly[0]['temperature'],
            "current_forecast": self.forecast_hourly[0]['shortForecast'],
            "temperature_unit": self.forecast_hourly[0]['temperatureUnit'],
            "forecast_12hr": self.forecast[0]['detailedForecast'],
            "forecast_7_day": self.forecast[1:]  # skip current period
        }

# shows the html on main localhost page
@app.route("/")
def home():
    return render_template("index.html")

# sends json of the data to the frontend at localhost:5000/api/weather
@app.route("/api/weather")
def get_weather():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    city = request.args.get('city')
    state = request.args.get('state')
    state_name = request.args.get('state_name')
    
    l = LocationData()

    if lat and lon:
        # if coordinates provided (from search system)
        l.lat = float(lat)
        l.lon = float(lon)
        
        # use the provided city/state info from the search results
        if city:
            l.city = city
        if state:
            l.state = state
        if state_name:
            l.state_name = state_name
            
        try:
            w = WeatherData(l.lat, l.lon)
        except Exception as e:
            return jsonify({
                "location": l.to_dict(),
                "weather": {"error": f"Failed to get weather data: {str(e)}"}
            })
    else:
        # use ip location
        l.get_user_location()
        w = WeatherData(l.lat, l.lon)

    return jsonify({
        "location": l.to_dict(),
        "weather": w.to_dict()
    })

# location search
@app.route("/api/search")
def search_locations():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "No search query provided", "results": []})
    
    l = LocationData()
    results = l.search_location(query)
    return jsonify({"results": results})

def main() -> None:
    # example usage

    l = LocationData()
    l.get_user_location()
    w = WeatherData(l.lat, l.lon)

    # prints city and state
    print(f"Weather data for {l.city}, {l.state}:\n")

    # prints the current temperature and weather
    print(f"Current Temperature: {w.forecast_hourly[0]['shortForecase']}\n")
    print(f"Current Weather: {w.forecast_hourly[0]['temperature']}°{w.forecast_hourly[0]['temperatureUnit']}\n")

    # prints the forecast for the current 12hr period
    print(f"Current 12hr Weather Forecast: {w.forecast[0]['detailedForecast']}\n")

    #prints the temperature and weather over the next 7 days
    print("7 day forecast:")
    for i in range(1, len(w.forecast)):
        print(f"{w.forecast[i]['name']}:")
        print(f"{w.forecast[i]['detailedForecast']}")

if __name__ == "__main__":
    app.run(debug=True)

'''
Important URLs:
https://api.weather.gov/gridpoints/SGF/121,69/forecast
https://api.weather.gov/gridpoints/SGF/121,69/forecast/hourly
'''
