import logging
from terra.base_client import Terra
from config import TERRA_API_KEY, TERRA_DEV_ID, TERRA_SECRET

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger("app")

terra = Terra(api_key=TERRA_API_KEY, dev_id=TERRA_DEV_ID, secret=TERRA_SECRET)


def generate_widget_session(reference_id):
    try:
        widget_response = terra.generate_widget_session(
            reference_id=reference_id,
            providers=["Fitbit"],
            auth_success_redirect_url="https://success.url",
            auth_failure_redirect_url="https://failure.url",
            language="en",
        ).get_parsed_response()
        print(widget_response)
        return widget_response.url
    except Exception as e:
        print(f"Error generating widget session: {str(e)}")
        return None


def get_user_trends(terra_user_id):
    # Implement Terra API calls to fetch user trends
    # This is a placeholder function
    return {
        "sleep": [7, 6, 8, 7, 6],
        "stress": [3, 4, 2, 3, 5],
        "exercise": [30, 45, 60, 30, 45],
    }


if __name__ == "__main__":
    generate_widget_session("test")
