#python code for backend
import requests

class LocationData():
    def __init__(self):
        self.state = ""
        self.state_name = ""
        self.city = ""
        self.zip_code = ""
        self.lat = ""
        self.lon = ""

    def get_user_location(self):
        try:
            r = requests.get("http://ip-api.com/json/").json()
        except:
            raise Exception("Could not get user location")
            
        self.state = r["region"]
        self.state_name = r["regionName"]
        self.city = r["city"]
        self.zip_code = r["zip"]
        self.lat = r["lat"]
        self.lon = r["lon"]
    
    def search_location(self):
        # to-do
        pass
    

def main() -> None:
    l = LocationData()
    l.get_user_location()
    print("State:", l.state)
    print("State Name:", l.state_name)
    print("City:", l.city)
    print("Zip Code:", l.zip_code)
    print("Latitude:", l.lat)
    print("Longitude:", l.lon)
    

if __name__ == "__main__":
    main()
