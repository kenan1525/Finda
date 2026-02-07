import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
FLIGHT_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"


def get_access_token():
    """Fetch Amadeus access token. Returns dict with 'access_token' or 'error'."""
    data = {
        "grant_type": "client_credentials",
        "client_id": getattr(settings, "AMADEUS_API_KEY", ""),
        "client_secret": getattr(settings, "AMADEUS_API_SECRET", ""),
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        resp = requests.post(TOKEN_URL, data=data, headers=headers, timeout=10)
        resp.raise_for_status()
        body = resp.json()
        token = body.get("access_token")
        if not token:
            return {"error": "no_access_token"}
        return {"access_token": token}
    except requests.RequestException as exc:
        logger.exception("Failed to fetch access token")
        return {"error": str(exc)}


def search_flights(origin, destination, date, adults=1):
    """Search flights via Amadeus. Returns dict with results or error."""
    if not origin or not destination or not date:
        return {"error": "missing_parameters"}

    origin_code = origin.strip().upper()
    destination_code = destination.strip().upper()

    token_resp = get_access_token()
    if token_resp.get("error"):
        return {"error": f"token_error: {token_resp.get('error')}"}

    token = token_resp.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "originLocationCode": origin_code,
        "destinationLocationCode": destination_code,
        "departureDate": date,
        "adults": adults,
        "max": 5,
    }

    try:
        resp = requests.get(FLIGHT_URL, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        logger.exception("Flight search failed")
        return {"error": str(exc)}
