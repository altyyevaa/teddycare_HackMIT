import requests
from terra.base_client import Terra

TERRA_API_KEY = "bYY_oG_vvUo5bK8LUgg5N47dcmg2zjk_"
TERRA_DEV_ID = "4actk-swing-testing-WwNOgPcxJ8"
TERRA_SECRET = ""


def get_user_trends(terra_user_id):
    # Implement Terra API calls to fetch user trends
    # This is a placeholder function
    return {
        "sleep": [7, 6, 8, 7, 6],
        "stress": [3, 4, 2, 3, 5],
        "exercise": [30, 45, 60, 30, 45],
    }

terra = Terra(TERRA_API_KEY, TERRA_DEV_ID, TERRA_SECRET)

auth_resp = terra.generate_authentication_url(
    reference_id="USER ID IN YOUR APP",
    resource="FITBIT",
    auth_success_redirect_url="https://success.url",
    auth_failure_redirect_url="https://failure.url",
).get_parsed_response()



# parsed_api_response = terra.list_providers().get_parsed_response()
# parsed_api_response = terra.list_users().get_parsed_response()


if __name__ == "__main__":
    print(auth_resp)
