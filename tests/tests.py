import sys
import types
import os

# ──────────────── stub out Flask & CORS ────────────────
class DummyFlask:
    def __init__(self, *args, **kwargs):
        pass

    # decorator for routes – just return the function unchanged
    def route(self, *args, **kwargs):
        def decorator(fn):
            return fn
        return decorator

    def run(self, *args, **kwargs):
        pass

def dummy_jsonify(x):
    return x

def dummy_render_template(template, **ctx):
    return ""

# inject into sys.modules before importing main.py
stub_flask = types.ModuleType("flask")
stub_flask.Flask = DummyFlask
stub_flask.jsonify = dummy_jsonify
stub_flask.render_template = dummy_render_template
sys.modules["flask"] = stub_flask

stub_cors = types.ModuleType("flask_cors")
stub_cors.CORS = lambda app, *args, **kwargs: None
sys.modules["flask_cors"] = stub_cors

# ───────── ensure project root is on sys.path ─────────
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root not in sys.path:
    sys.path.insert(0, root)

# ────────────── import the code under test ──────────────
from main import LocationData, WeatherData

def test_location_to_dict_and_search_stub():
    ld = LocationData()
    # manually prime its fields
    ld.state      = "FL"
    ld.state_name = "Florida"
    ld.city       = "Miami"
    ld.lat        = 25.7617
    ld.lon        = -80.1918

    assert ld.to_dict() == {
        "state":      "FL",
        "state_name": "Florida",
        "city":       "Miami",
        "lat":         25.7617,
        "lon":        -80.1918
    }

    # stub: should return None until implemented
    assert ld.search_location() is None

def test_weather_to_dict_mapping():
    # bypass update_weather by constructing a raw instance
    wd = WeatherData.__new__(WeatherData)

    # fake the raw data lists
    wd.forecast = [
        {"detailedForecast": "Now!"},
        {"name": "Tomorrow", "detailedForecast": "Sunny skies"}
    ]
    wd.forecast_hourly = [
        {"temperature": 80, "shortForecast": "Clear",  "temperatureUnit": "F"},
        {"temperature": 75, "shortForecast": "Cloudy","temperatureUnit": "F"}
    ]

    out = wd.to_dict()
    assert out["current_temperature"] == 80
    assert out["current_forecast"]    == "Clear"
    assert out["temperature_unit"]    == "F"
    assert out["forecast_12hr"]       == "Now!"
    # skip index 0 for the 7-day list
    assert out["forecast_7_day"] == [
        {"name": "Tomorrow", "detailedForecast": "Sunny skies"}
    ]
