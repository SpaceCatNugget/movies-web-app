from search_db import normalize_title, search_exact, search_fuzzy
from search_omdb import get_exact_imdb_suggestions

def get_rating_result(user_input: str) -> list:
    """
    Combines database and OMDb searches for a movie title.
    Returns a deduplicated list of results, prioritizing OMDb data if available.
    """
    if not user_input:
        return []

    normalized_input = normalize_title(user_input)

    exact_db_results = search_exact(normalized_input)
    fuzzy_db_results = search_fuzzy(normalized_input)

    omdb_results = get_exact_imdb_suggestions(user_input)

    combined = exact_db_results + fuzzy_db_results + omdb_results
    final_results = {}
    for movie in combined:
        title = movie['title']
        if title not in final_results:
            final_results[title] = movie
        elif movie.get('source') == 'omdb':
            final_results[title] = movie

    if final_results:
        return list(final_results.values())

    return [{
        "title": user_input,
        "message": "Movie not found",
        "avg_rating": None,
        "omdb_ratings": {},
        "source": "not_found"
    }]