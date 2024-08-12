import requests
import json
from datetime import datetime
import argparse
import os
from dotenv import load_dotenv
import pandas as pd
import threads_payload


load_dotenv()


def get_threads_post_reply(
    post_id: str,
    fb_dtsg: str,
) -> dict:
    """
    Fetches and processes replies to a Threads post.

    This function makes paginated API requests to retrieve all replies to a specific
    Threads post. It processes the response data and extracts relevant information
    about each reply, including user details, post content, and engagement metrics.

    Args:
        post_id (str): The unique identifier of the Threads post to fetch replies for.
        fb_dtsg (str): The Facebook DTSG token required for authentication.

    Returns:
        Dict[str, Dict]: A dictionary where each key is a reply post ID and the value
        is a dictionary containing detailed information about that reply, including:
        - id: The unique identifier of the reply post
        - code: The code associated with the reply post
        - timestamp: The creation time of the reply
        - like_count: The number of likes on the reply
        - direct_reply_count: The number of direct replies to this reply
        - repost_count: The number of reposts of this reply
        - quote_count: The number of quote posts of this reply
        - user_id: The ID of the user who posted the reply
        - username: The username of the user who posted the reply
        - is_verified: Whether the user is verified
        - profile_pic_url: URL of the user's profile picture
        - text: The text content of the reply (if any)
        - media_type: The type of media attached to the reply
        - accessibility_caption: The accessibility caption for any media
        - img_urls: List of URLs for any images in the reply

    Raises:
        requests.exceptions.RequestException: If there's an error in making the API request
        or processing the response.

    Note:
        This function relies on environment variables for authentication headers and
        makes use of pagination to retrieve all replies. It handles potential errors
        in API requests but may not capture all possible edge cases.
    """

    url = "https://www.threads.net/api/graphql"

    headers = {
        "cookie": os.getenv("COOKIE"),
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "threads-client",
        "x-ig-app-id": "238260118697367",
    }

    all_scraped_data = {}
    end_cursor = None
    has_next_page = True

    while has_next_page:
        data = {
            "fb_dtsg": fb_dtsg,
            "doc_id": "8146902565367397",
        }

        variables = {
            "postID": post_id,
            "__relay_internal__pv__BarcelonaIsLoggedInrelayprovider": True,
            "__relay_internal__pv__BarcelonaShouldShowFediverseM1Featuresrelayprovider": True,
            "__relay_internal__pv__BarcelonaIsInlineReelsEnabledrelayprovider": True,
            "__relay_internal__pv__BarcelonaUseCometVideoPlaybackEnginerelayprovider": False,
            "__relay_internal__pv__BarcelonaOptionalCookiesEnabledrelayprovider": False,
            "__relay_internal__pv__BarcelonaShowReshareCountrelayprovider": False,
            "__relay_internal__pv__BarcelonaQuotePostImpressionLoggingEnabledrelayprovider": False,
            "__relay_internal__pv__BarcelonaShouldShowFediverseM075Featuresrelayprovider": True,
        }

        if end_cursor:
            variables["after"] = end_cursor["end_cursor"]

        data["variables"] = json.dumps(variables)

        try:
            with requests.post(url, headers=headers, data=data) as response:

                response.raise_for_status()

                response = response.json()

                threads_replies = response["data"]["data"]["edges"]
                page_info = response["data"]["data"]["page_info"]
                has_next_page = page_info["has_next_page"]
                end_cursor = page_info

                for threads_reply in threads_replies:
                    post = threads_reply["node"]["thread_items"][0]["post"]

                    detail = {
                        "id": post["id"],
                        "code": post["code"],
                        "timestamp": datetime.fromtimestamp(post["taken_at"]).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "like_count": post["like_count"],
                        "direct_reply_count": post["text_post_app_info"][
                            "direct_reply_count"
                        ],
                        "repost_count": post["text_post_app_info"]["repost_count"],
                        "quote_count": post["text_post_app_info"]["quote_count"],
                        "user_id": post["user"]["id"],
                        "username": post["user"]["username"],
                        "is_verified": post["user"]["is_verified"],
                        "profile_pic_url": post["user"]["profile_pic_url"],
                        "text": (
                            post["caption"]["text"]
                            if post.get("caption") and post["caption"].get("text")
                            else None
                        ),
                        "media_type": post["media_type"],
                        "accessibility_caption": post["accessibility_caption"],
                        "img_urls": [
                            img["url"] for img in post["image_versions2"]["candidates"]
                        ],
                    }

                    all_scraped_data[post["id"]] = detail

        except requests.exceptions.RequestException as e:
            print("Failed to get reply data: ", e)

    return all_scraped_data


def save_data(
    data: dict, post_id: str, output_file_type: str = "json", output_dir: "str" = "data"
) -> None:
    """
    Saves the provided data to a file in the specified format and directory.

    This function takes a dictionary of data and saves it to a file. The file format
    can be JSON, CSV, or XLSX. The function creates the output directory if it doesn't
    exist and uses a timestamp in the filename to ensure uniqueness.

    Args:
        data (dict): The data to be saved. Expected to be a dictionary where each key
                     represents a unique entry.
        post_id (str): The threads post_id.
        output_file_type (str, optional): The desired output file format.
                                          Options are "json", "csv", or "xlsx".
                                          Defaults to "json".
        output_dir (str, optional): The directory where the output file will be saved.
                                    Defaults to "data".

    Returns:
        None

    Raises:
        ValueError: If an unsupported output_file_type is provided.

    Note:
        - The function uses the current timestamp in the filename to avoid overwriting.
        - For CSV and XLSX formats, the data is converted to a pandas DataFrame.
        - The function prints the location of the saved file and the total number of entries.

    Example:
        >>> data = {"entry1": {"field1": "value1"}, "entry2": {"field1": "value2"}}
        >>> post_id = "3422371711650451662"
        >>> save_data(data, post_id, output_file_type="csv", output_dir="output")
        Threads replies already save as output/2023-08-12_15-30-45.csv
        Total data: 2
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{output_dir}/{current_timestamp}_{post_id}"

    if output_file_type.lower() == "json":
        with open(f"{filename}.json", "w") as json_file:
            json.dump(data, json_file, indent=2)
        print(f"Threads replies already save as {filename}.json")

    elif output_file_type.lower() == "csv":
        df = pd.DataFrame.from_dict(data, orient="index")
        df.to_csv(f"{filename}.csv", index=False)
        print(f"Threads replies already save as {filename}.csv")

    elif output_file_type.lower() == "xlsx":
        df = pd.DataFrame.from_dict(data, orient="index")
        df.to_excel(f"{filename}.xlsx", index=False)
        print(f"Threads replies already save as {filename}.xlsx")

    print(f"Total data: {len(data)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Get reply from Threads Post")
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="URL Threads post, ex: https://www.threads.net/@zuck/post/C9-tPByRVDO",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "csv", "xlsx"],
        default="json",
        help="Output file format, options: json, csv, xlsx (default: json)",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="data",
        help="Output file directory (default: data)",
    )

    args = parser.parse_args()

    payload = threads_payload.get_threads_required_payload(args.url)

    scraped_data = get_threads_post_reply(
        payload["post_id"],
        payload["fb_dtsg"],
    )

    save_data(
        data=scraped_data,
        post_id=payload["post_id"],
        output_file_type=args.format,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
