import requests
from urllib.parse import quote_plus
import os

OMDB_API_KEY = os.getenv("OMDB_API_KEY")
omdb_cache = {}

def get_omdb_info(title: str) -> dict:
    """
    Exact title search on OMDb.
    Returns detailed info including IMDb, Rotten Tomatoes, Metacritic ratings.
    Caches results to avoid repeated API calls.
    """
    if not OMDB_API_KEY:
        return {}

    title_key = title.lower()
    if title_key in omdb_cache:
        return omdb_cache[title_key]

    encoded_title = quote_plus(" ".join(title.strip().split()).title())
    url = f"https://www.omdbapi.com/?t={encoded_title}&apikey={OMDB_API_KEY}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("Response") != "True":
            omdb_cache[title_key] = {}
            return {}

        ratings_dict = {}
        for r in data.get("Ratings", []):
            source = r["Source"].lower().replace(" ", "_")
            if "internet_movie_database" in source:
                source = "imdb"
            elif "rotten_tomatoes" in source:
                source = "rotten_tomatoes"
            elif "metacritic" in source:
                source = "metacritic"
            ratings_dict[source] = r["Value"]

        result = {
            "title": data.get("Title"),
            "year": data.get("Year"),
            "plot": data.get("Plot"),
            "poster": data.get("Poster"),
            "omdb_ratings": ratings_dict,
            "source": "omdb"
        }
        omdb_cache[title_key] = result
        return result
    except Exception as e:
        print(f"[OMDb ERROR] {title}: {e}")
        omdb_cache[title_key] = {}
        return {}

def search_omdb_fuzzy(query: str, limit: int = 5) -> list:
    """
    Fuzzy search on OMDb using the 's' search parameter.
    Returns a list of movies with basic info + detailed ratings.
    """
    if not OMDB_API_KEY:
        return []

    encoded_query = quote_plus(query)
    url = f"https://www.omdbapi.com/?s={encoded_query}&apikey={OMDB_API_KEY}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("Response") != "True":
            return []

        results = []
        for movie in data.get("Search", [])[:limit]:
            imdbID = movie["imdbID"]
            detail_url = f"https://www.omdbapi.com/?i={imdbID}&apikey={OMDB_API_KEY}"
            detail_resp = requests.get(detail_url, timeout=5).json()

            ratings_dict = {}
            for r in detail_resp.get("Ratings", []):
                source = r["Source"].lower().replace(" ", "_")
                if "internet_movie_database" in source:
                    source = "imdb"
                elif "rotten_tomatoes" in source:
                    source = "rotten_tomatoes"
                elif "metacritic" in source:
                    source = "metacritic"
                ratings_dict[source] = r["Value"]

            results.append({
                "title": detail_resp.get("Title"),
                "year": detail_resp.get("Year"),
                "plot": detail_resp.get("Plot"),
                "poster": detail_resp.get("Poster"),
                "omdb_ratings": ratings_dict,
                "source": "omdb"
            })

        return results
    except Exception as e:
        print(f"[OMDb ERROR] search_omdb_fuzzy for {query}: {e}")
        return []

def get_exact_imdb_suggestions(title: str) -> list:
    """
    Combines exact + fuzzy OMDb search.
    Returns deduplicated suggestions with avg_rating from IMDb if available.
    """
    results = []

    # Exact search
    exact = get_omdb_info(title)
    if exact:
        imdb_rating_str = exact['omdb_ratings'].get('imdb')
        avg_rating = float(imdb_rating_str.split('/')[0]) if imdb_rating_str else None
        results.append({**exact, "avg_rating": avg_rating})

    # Fuzzy search
    fuzzy = search_omdb_fuzzy(title)
    existing_titles = {r['title'] for r in results}
    for r in fuzzy:
        if r['title'] not in existing_titles:
            imdb_rating_str = r['omdb_ratings'].get('imdb')
            avg_rating = float(imdb_rating_str.split('/')[0]) if imdb_rating_str else None
            results.append({**r, "avg_rating": avg_rating})

    return results
