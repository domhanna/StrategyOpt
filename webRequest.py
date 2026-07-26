import requests
from bs4 import BeautifulSoup

def web_request(base_url, headers=None, params = None):

    """
    Fetch a URL with a browser-like User-Agent and parse it with BeautifulSoup.

    Args:
        base_url (str): The URL to request.
        headers (dict, optional): Request headers to send. Defaults to a
            generic browser User-Agent if not provided.

    Returns:
    tuple[bs4.BeautifulSoup, str]:
        soup (bs4.BeautifulSoup): Parsed HTML content of the response.
        final_url (str): The final resolved URL of the response, after
            any redirects and query parameters — useful as a base for
            urljoin() when resolving relative links found in the page.

    Raises:
        requests.HTTPError: If the response status is 4xx/5xx.
    """

    headers = headers or {"User-Agent": "Mozilla/5.0"}
    response = requests.get(base_url, headers=headers, params=params)
    print(response.url, "\n\n")

    response.raise_for_status()

    html = response.text
    soup = BeautifulSoup(html, "lxml")
    final_url = response.url

    return soup, final_url