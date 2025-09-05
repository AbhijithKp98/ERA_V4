import requests

BASE_URL = "https://world.openfoodfacts.org/api/v0/product/{}.json"
SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"

def search_product(query, page_size=5):
    """
    Search products by name.
    """
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": page_size
    }
    res = requests.get(SEARCH_URL, params=params)
    res.raise_for_status()
    return res.json().get("products", [])


def get_product(barcode):
    """
    Get product details by barcode.
    """
    res = requests.get(BASE_URL.format(barcode))
    res.raise_for_status()
    return res.json().get("product", {})
