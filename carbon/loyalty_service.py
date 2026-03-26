from .loyalty_client import LoyaltyAPIClient

class LoyaltyService:
    """Service layer between CarbonCloud views and Loyalty API."""

    ACTIVITY_RULE_MAP = {
        "transport": "carbon_transport",
        "electricity": "carbon_electricity",
        "food": "carbon_food",
        "shopping": "carbon_shopping",
    }

    ERROR_NOT_CONNECTED = {"success": False, "error": "Not connected"}

    @staticmethod
    def is_connected(request):
        return request.session.get("loyalty_user_id") is not None

    @staticmethod
    def get_loyalty_user_id(request):
        return request.session.get("loyalty_user_id")

    @staticmethod
    def connect_user(request, username, password):
        """Log in a user and store session data if successful."""
        client = LoyaltyAPIClient()
        result = client.login_user(username, password)

        if result.get("success"):
            request.session["loyalty_user_id"] = result["data"]["user_id"]
            request.session["loyalty_username"] = result["data"]["username"]

        # Always return result from API; caller can check success
        return result

    @staticmethod
    def register_and_connect(request, username, email, password, first_name="", last_name=""):
        """Register a new user and log them in if successful."""
        client = LoyaltyAPIClient()
        result = client.register_user(username, email, password, first_name, last_name)

        if result.get("success"):
            request.session["loyalty_user_id"] = result["data"]["user_id"]
            request.session["loyalty_username"] = result["data"]["username"]

        return result

    @staticmethod
    def disconnect(request):
        request.session.pop("loyalty_user_id", None)
        request.session.pop("loyalty_username", None)

    @staticmethod
    def get_balance(request):
        user_id = request.session.get("loyalty_user_id")
        if not user_id:
            return LoyaltyService.ERROR_NOT_CONNECTED
        client = LoyaltyAPIClient()
        return client.get_balance(user_id)

    @staticmethod
    def get_summary(request):
        user_id = request.session.get("loyalty_user_id")
        if not user_id:
            return LoyaltyService.ERROR_NOT_CONNECTED
        client = LoyaltyAPIClient()
        return client.get_summary(user_id)

    @staticmethod
    def award_points_for_entry(request, entry):
        user_id = request.session.get("loyalty_user_id")
        if not user_id:
            return {"success": False, "error": "Not connected to loyalty"}

        activity_code = LoyaltyService.ACTIVITY_RULE_MAP.get(entry.activity_type)
        if not activity_code:
            return {"success": False, "error": "No rule for this activity"}

        client = LoyaltyAPIClient()
        return client.earn_by_rule(
            user_id=user_id,
            activity_code=activity_code,
            reference_id=f"carbon-entry-{entry.id}",
            source="carboncloud",
        )

    @staticmethod
    def get_transactions(request, limit=20):
        user_id = request.session.get("loyalty_user_id")
        if not user_id:
            return LoyaltyService.ERROR_NOT_CONNECTED
        client = LoyaltyAPIClient()
        return client.get_transactions(user_id, limit)

    @staticmethod
    def get_leaderboard():
        client = LoyaltyAPIClient()
        return client.get_leaderboard()