# services/currency_service.py

import requests

class CurrencyService:
    @staticmethod
    def convert_points_to_currency(points: int, currency: str = "EUR") -> float:
        """
        Converts loyalty points to a currency value.
        Example: 100 points = 1 EUR (default conversion rate)
        You can also connect this to a public API for dynamic conversion.
        """
        # Simple fixed conversion rate: 100 points = 1 EUR
        conversion_rate = 0.01  # 1 point = 0.01 EUR
        value = points * conversion_rate

        # Round to 2 decimal places
        return round(value, 2)

