import requests
from flask import Blueprint, request, jsonify
import logging

from ..config import Config
from ..utils.decorators import token_required

weather_bp = Blueprint('weather', __name__, url_prefix='/api/weather')

# Weather API URLs from APISpace
HOURLY_WEATHER_URL = "https://eolink.o.apispace.com/456456/weather/v001/hour"
CITY_SEARCH_URL = "https://eolink.o.apispace.com/456456/function/v001/city"


@weather_bp.route('/search', methods=['GET'])
@token_required
def search_city(current_user):
    city_name = request.args.get('city')
    if not city_name:
        return jsonify({"error": "City parameter is required"}), 400

    logging.info(f"--- Attempting to search for city: {city_name} ---")

    try:
        headers = {
            "X-APISpace-Token": Config.API_SPACES_API_KEY
        }
        params = {
            "location": city_name,
            "area": "china",
            "items": 10
        }
        
        logging.info(f"Requesting URL: {CITY_SEARCH_URL} with params: {params}")
        response = requests.get(CITY_SEARCH_URL, headers=headers, params=params)
        logging.info(f"External API response status: {response.status_code}")
        logging.info(f"External API response body: {response.text}")

        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()

        if data.get("status") == 0 and "areaList" in data:
            logging.info("City search successful, returning area list.")
            return jsonify(data["areaList"])
        else:
            # Look for potential error messages from the API
            error_message = data.get("message", "Failed to find city.")
            logging.error(f"External API returned a logical error: {error_message}")
            return jsonify({"error": error_message}), 500

    except requests.exceptions.RequestException as e:
        logging.error(f"Exception during request to external weather API: {e}")
        return jsonify({"error": f"Error calling weather API: {e}"}), 502
    except Exception as e:
        logging.error(f"An unexpected error occurred in search_city: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500


@weather_bp.route('/hourly', methods=['GET'])
@token_required
def get_hourly_weather(current_user):
    areacode = request.args.get('areacode')
    hours = request.args.get('hours', 24)  # Default to 24 hours
    if not areacode:
        return jsonify({"error": "areacode parameter is required"}), 400

    headers = {
        "X-APISpace-Token": Config.API_SPACES_API_KEY
    }
    params = {
        "areacode": areacode,
        "hours": hours
    }

    try:
        response = requests.get(HOURLY_WEATHER_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Check if the API call was successful and the 'result' key exists
        if data.get("status") == 0 and "result" in data:
            return jsonify(data["result"])
        else:
            # Forward the error from the external API if possible
            error_message = data.get("message", "Failed to fetch weather data from external source.")
            return jsonify({"error": error_message}), 500
            
    except requests.exceptions.RequestException as e:
        print(f"Error calling hourly weather API: {e}")
        return jsonify({"error": "Failed to fetch weather data"}), 502
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500