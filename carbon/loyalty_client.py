import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class LoyaltyAPIClient:
    """HTTP client for the Loyalty Points API."""

    def __init__(self):
        self.base_url = settings.LOYALTY_API_BASE_URL
        self.timeout = 10

    def _request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault("timeout", self.timeout)
        try:
            resp = getattr(requests, method)(url, **kwargs)
            data = resp.json()
            if resp.ok:
                return {"success": True, "data": data}
            return {"success": False, "error": data.get("error", resp.text)}
        except requests.ConnectionError:
            logger.warning(f"Loyalty API unreachable: {url}")
            return {"success": False, "error": "Loyalty API is unreachable"}
        except requests.Timeout:
            return {"success": False, "error": "Loyalty API timed out"}
        except Exception as e:
            logger.error(f"Loyalty API error: {e}")
            return {"success": False, "error": str(e)}

    def health(self):
        return self._request("get", "/health/")

    def register_user(self, username, email, password, first_name="", last_name=""):
        return self._request("post", "/register/", json={
            "username": username,
            "email": email,
            "password": password,
            "password_confirm": password,
            "first_name": first_name,
            "last_name": last_name,
        })

    def login_user(self, username, password):
        return self._request("post", "/login/", json={
            "username": username,
            "password": password,
        })

    def get_balance(self, user_id):
        return self._request("get", f"/balance/{user_id}/")

    def get_summary(self, user_id):
        return self._request("get", f"/summary/{user_id}/")

    def earn_points(self, user_id, points, description="", reference_id="", source="carboncloud"):
        return self._request("post", "/earn/", json={
            "user_id": user_id,
            "points": points,
            "description": description,
            "reference_id": reference_id,
            "source_service": source,
        })

    def earn_by_rule(self, user_id, activity_code, reference_id="", source="carboncloud"):
        return self._request("post", "/earn-by-rule/", json={
            "user_id": user_id,
            "activity_code": activity_code,
            "reference_id": reference_id,
            "source_service": source,
        })

    def get_transactions(self, user_id, limit=20):
        return self._request("get", f"/transactions/{user_id}/?limit={limit}")

    def get_leaderboard(self, limit=10):
        return self._request("get", f"/leaderboard/?limit={limit}")