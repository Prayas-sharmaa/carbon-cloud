import requests
from datetime import datetime

class CarbonIntensityService:
    API_URL = "https://api.carbonintensity.org.uk/intensity"

    @staticmethod
    def get_current_intensity():
        try:
            resp = requests.get(CarbonIntensityService.API_URL, timeout=5)
            resp.raise_for_status()
            data = resp.json()

            if "data" in data and len(data["data"]) > 0:
                intensity = data["data"][0]["intensity"]
                return {
                    "forecast": intensity.get("forecast"),
                    "actual": intensity.get("actual"),
                    "index": intensity.get("index"),
                    "from": data["data"][0].get("from"),
                    "to": data["data"][0].get("to"),
                    "error": None,
                }
            else:
                return {"error": "No data found"}
        except Exception as e:
            return {"error": str(e)}