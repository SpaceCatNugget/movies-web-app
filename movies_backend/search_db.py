import pandas as pd
import re
from rapidfuzz import process, fuzz

# Load datasets
movies = pd.read_csv('dataset/u_item.csv')
ratings = pd.read_csv('dataset/u_data.csv')
df = pd.merge(
    ratings,
    movies[['movie_id', 'movie_title']],
    left_on='item_id',
    right_on='movie_id'
)

# Normalize movie titles once
def normalize_title(title: str) -> str:
    title = title.lower().strip()
    title = re.sub(r'\(.*?\)', '', title)  # remove anything inside ()
    title = re.sub(r'[^a-z0-9 ]', '', title)  # remove other punctuation
    title = re.sub(r'\s+', ' ', title)  # collapse multiple spaces
    return title

df['movie_title_normalized'] = df['movie_title'].apply(normalize_title)

# ---- Search functions ----
def search_exact(normalized_title: str) -> list:
    """
    Returns exact matches from the DB with average rating.
    """
    matches = df[df['movie_title_normalized'] == normalized_title]
    if matches.empty:
        return []

    grouped = matches.groupby('movie_title')['rating'].mean().reset_index()
    results = []
    for _, row in grouped.iterrows():
        results.append({
            "title": row['movie_title'],
            "avg_rating": round(row['rating'], 2),
            "source": "db"
        })
    return results

def find_closest_movie(user_input: str, movie_titles: list, limit=5,
                       threshold=90) -> list:
    """
    Uses RapidFuzz to find closest matches in movie titles.
    """
    results = process.extract(query=user_input, choices=movie_titles,
                              scorer=fuzz.WRatio, limit=limit)
    return [(title, score, idx) for title, score, idx in results
            if score >= threshold]

def search_fuzzy(normalized_input: str) -> list:
    """
    Returns fuzzy-matched movies from DB with average ratings.
    """
    movie_titles_normalized = df['movie_title_normalized'].unique()
    closest_matches = find_closest_movie(normalized_input, movie_titles_normalized)
    closest_matches.sort(key=lambda x: x[1], reverse=True)

    results = []
    for normalized_title, score, _ in closest_matches:
        original_title = df[df['movie_title_normalized'] ==
                            normalized_title]['movie_title'].iloc[0]
        match_ratings = df[df['movie_title'] == original_title]['rating']
        avg_rating = round(match_ratings.mean(), 2) if not match_ratings.empty\
            else None
        results.append({
            "title": original_title,
            "avg_rating": avg_rating,
            "source": "db"
        })
    return results
