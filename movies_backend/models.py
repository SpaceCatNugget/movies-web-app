from typing import Optional, Tuple, List
from dataclasses import dataclass

from combined_search import get_rating_result


# -------------------------------
# Core Data Structures
# -------------------------------

@dataclass
class Config:
    database: Optional[str] = None
    filters: Optional[dict] = None


class Movie:
    def __init__(self, name: str):
        self.name = name


class StrMovie(Movie):
    """Simple movie identified by its title."""
    pass


# -------------------------------
# Functional Layer
# -------------------------------

def get_rating(movie: Movie, config: Optional[Config] = None) -> list[dict]:
    """Returns a ranked list of results with 'avg_rating', 'source', etc."""
    try:
        results = get_rating_result(movie.name)
        if not results:
            raise MovieNameError(f"No results found for '{movie.name}'")
        return results
    except Exception as e:
        raise DataBaseError(f"Failed to get combined ratings: {e}")


def get_info(movie: Movie) -> dict:
    """
    Get detailed info for a movie (from the combined results).
    Just returns the first exact match if available.
    """
    results = get_rating_result(movie.name)
    if not results:
        raise MovieNameError(f"No info found for '{movie.name}'")
    return results[0]  # first match = best candidate


def get_top_x(num: int = 10, config: Optional[Config] = None) -> List[Tuple[Movie, float]]:
    """
    returns a list of top num movies.
    """
    try:
        results = get_rating_result("")
        sorted_results = sorted(results, key=lambda x: x.get("avg_rating", 0) or 0, reverse=True)
        top_movies = [
            (StrMovie(r["title"]), r["avg_rating"]) for r in sorted_results[:num]
        ]
        return top_movies
    except Exception as e:
        raise DataBaseError(f"Failed to get top movies: {e}")


# -------------------------------
# Custom Errors
# -------------------------------

class MovieNameError(ValueError):
    pass


class DataBaseError(ValueError):
    pass
