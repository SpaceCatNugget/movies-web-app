from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv

from models import StrMovie, get_rating
from search_omdb import get_exact_imdb_suggestions

# Load environment variables
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return '<h2>🎬 Movie Ratings API is running!</h2><p>Use POST /api/get_rating</p>'


@app.route('/api/get_rating', methods=['POST'])
def api_get_rating():
    user_input = request.json.get('title', '').strip()
    if not user_input:
        return jsonify([])

    movie = StrMovie(user_input)
    try:
        results = get_rating(movie)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/get_omdb_exact', methods=['POST'])
def api_get_omdb_exact():
    user_input = request.json.get('title', '').strip()
    if not user_input:
        return jsonify([])

    results = get_exact_imdb_suggestions(user_input)
    return jsonify(results)


@app.route('/api/top_ten', methods=['GET'])
def api_top_ten():
    """
    Returns the top 10 movies by vote_average from TMDb
    """
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "sort_by": "vote_average.desc",
        "vote_count.gte": 1000,
        "language": "en-US",
        "page": 1
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        top_ten = []
        for movie in data.get("results", [])[:10]:
            top_ten.append({
                "title": movie.get("title"),
                "rating": movie.get("vote_average"),
                "overview": movie.get("overview"),
                "poster": f"https://image.tmdb.org/t/p/w500"
                          f"{movie['poster_path']}"
                if movie.get("poster_path") else None,
                "release_date": movie.get("release_date")
            })

        return jsonify(top_ten)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
