import requests
from django.conf import settings


class CloudMailService:

    @staticmethod
    def send_email(to_email, subject, message, from_name="CarbonCloud"):

        url = f"{settings.CLOUDMAIL_API_URL}/api/send/"

        data = {
            "to_email": to_email,
            "subject": subject,
            "message": message,
            "from_name": from_name,
            "reply_to": "support@carboncloud.com"
        }

        try:
            response = requests.post(url, data=data)

            # Debug logging
            print("CloudMail STATUS:", response.status_code)
            print("CloudMail RESPONSE:", response.text)

            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json()
                }

            return {
                "success": False,
                "error": response.text
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }