import requests
from bs4 import BeautifulSoup
import json
import jsonpath_ng as jp
from dotenv import load_dotenv
import os


load_dotenv()


def get_threads_required_payload(url: str) -> dict:
    """
    Fetches required payload information from a given Threads URL.

    This function makes a GET request to the provided Threads URL and extracts
    necessary payload information, including the post ID and Facebook DTSG token.

    Args:
        url (str): The URL of the Threads post.

    Returns:
        dict: A dictionary containing:
            - 'post_id': The unique identifier of the post.
            - 'fb_dtsg': The Facebook DTSG token.

    Raises:
        requests.exceptions.RequestException: If there's an error in making the request
            or processing the response.

    Note:
        This function relies on environment variables for authentication headers.
    """

    headers = {
        "cookie": os.getenv("COOKIE"),
        "user-agent": "threads-client",
    }

    try:
        with requests.get(url=url, headers=headers) as response:

            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            payload = {"post_id": None, "fb_dtsg": None}

            payload["post_id"] = get_post_id(soup)
            payload["fb_dtsg"] = get_fb_dtsg(soup)

            print(payload)

            return payload

    except requests.exceptions.RequestException as e:
        print("Failed to get required payload: ", e)


def get_post_id(soup: BeautifulSoup) -> str:
    """
    Extracts the post ID from the HTML soup of a Threads page.

    This function searches for a script tag containing the post ID in the parsed HTML,
    then uses JSONPath to extract the post ID from the JSON data within the script.

    Args:
        soup (BeautifulSoup): Parsed HTML content of the Threads page.

    Returns:
        str: The post ID if found, None otherwise.
    """

    script_tags = soup.find_all("script")

    for script in script_tags:
        script_content = script.string

        if script_content and "post_id" in script_content:
            try:
                post_id_script = json.loads(script_content)
                post_id_expr = jp.parse("$..post_id")
                return [match.value for match in post_id_expr.find(post_id_script)][0]
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")

    print("Error: Could not find post_id")
    return None


def get_fb_dtsg(soup: BeautifulSoup) -> str:
    """
    Extracts the Facebook DTSG token from the HTML soup of a Threads page.

    This function looks for a specific script tag with id '__eqmc', parses its content
    as JSON, and extracts the Facebook DTSG token.

    Args:
        soup (BeautifulSoup): Parsed HTML content of the Threads page.

    Returns:
        str: The Facebook DTSG token if found, None otherwise.

    Raises:
        AttributeError: If the required script tag is not found.
        json.JSONDecodeError: If there's an error parsing the script content as JSON.
        KeyError: If the expected key is not found in the parsed JSON.
    """
    try:
        fb_dtsg_script = json.loads(soup.find("script", id="__eqmc").string)
        return fb_dtsg_script["f"]
    except (AttributeError, json.JSONDecodeError, KeyError) as e:
        print(f"Error get fb_dtsg: {e}")
        return None
