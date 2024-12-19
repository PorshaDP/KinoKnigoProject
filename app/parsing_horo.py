import csv
import random
from bs4 import BeautifulSoup
import requests
import sys

# Убедимся, что выводим текст в консоль с правильной кодировкой
sys.stdout.reconfigure(encoding='utf-8')

# Словарь для маппинга категорий на жанры
CATEGORY_GENRE_MAPPING = {
    "финансы": [
        "Action, Adventure, Sci-Fi",
        "Biography, Drama, History",
        "Crime, Drama, Mystery",
        "Biography, Drama",
        "Action, Crime, Thriller",
        "Crime, Drama, Thriller",
        "Comedy, Crime",
        "Mystery, Thriller",
        "Drama, Thriller",
        "Action, Crime, Drama",
        "Biography, Crime, Drama",
        "Drama, Mystery, Thriller",
        "Crime, Thriller",
        "Biography, Comedy, Drama",
        "Crime, Drama",
        "Adventure, Drama, Horror",
        "Adventure, Comedy, Music",
        "Horror, Mystery, Thriller",
        "Crime, Horror, Thriller",
        "Drama, Fantasy, Horror"
    ],
    "любовь": [
        "Comedy, Drama, Romance",
        "Drama, Romance",
        "Comedy, Romance",
        "Romance, Sci-Fi, Thriller",
        "Comedy, Music, Romance",
        "Biography, Drama, Romance",
        "Comedy, Fantasy, Romance",
        "Drama, Fantasy, Romance",
        "Drama, Romance, War",
        "Comedy, Crime, Romance",
        "Drama, Horror",
        "Adventure, Family, Fantasy",
        "Drama, Family, Fantasy",
        "Fantasy, Horror, Thriller",
        "Horror, Sci-Fi, Thriller"
    ],
    "здоровье": [
        "Drama, Sport",
        "Adventure, Drama, Family",
        "Biography, Drama, Sport",
        "Drama, History, Musical",
        "Drama, Romance, Sci-Fi",
        "Biography, Comedy, Drama",
        "Adventure, Biography, Drama",
        "Drama, Music",
        "Drama, History, War",
        "Comedy, Drama, Family",
        "Adventure, Family, Fantasy",
        "Comedy, Drama, Music",
        "Drama, Family, Fantasy",
        "Biography, Drama, Musical",
        "Biography, Drama, Sport",
        "Action, Adventure, Comedy",
        "Action, Adventure, Family",
        "Action, Adventure, Fantasy",
        "Animation, Adventure, Comedy",
        "Action, Adventure, Sci-Fi",
        "Adventure, Drama, Fantasy",
        "Adventure, Comedy, Drama",
        "Action, Horror, Sci-Fi",
        "Horror, Thriller",
        "Action, Fantasy, Horror"
    ]
}



def get_horoscope_and_top_category(sign):
    url = f"https://horo.mail.ru/prediction/{sign}/today/"
    response = requests.get(url)

    if response.status_code != 200:
        return None, None

    soup = BeautifulSoup(response.content, "html.parser")

    horoscope_text = None
    try:
        horoscope_div = soup.find("div", attrs={"article-item-type": "html"})
        horoscope_text = horoscope_div.find("p").get_text(strip=True)
    except AttributeError:
        pass

    categories = {}
    try:
        for block in soup.find_all("div", class_="a8eab328e5"):
            category_link = block.find("a", href=True)
            if category_link:
                category_name = category_link.text.strip()
                stars_block = block.find("ul", class_="b5ce145b7d")
                if stars_block and "aria-label" in stars_block.attrs:
                    stars = int(stars_block["aria-label"].split()[0])
                    categories[category_name] = stars

        top_category = max(categories, key=categories.get)
        top_stars = categories[top_category]
    except Exception:
        top_category, top_stars = None, None

    return horoscope_text, (top_category, top_stars)


def get_movies_for_category(top_category):
    genres = CATEGORY_GENRE_MAPPING.get(top_category.lower(), [])
    if not genres:
        return []

    movies = []
    try:
        with open("app/learning/THUMBNAILS_translated_movies.csv", newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if 'Genre' in row:
                    genre = row['Genre'].strip()
                    if genre in genres:
                        movie_data = {
                            "title": row['Title'].strip(),
                            "alt_name": row.get('alt_name', 'default_thumbnail.jpg'),  # Используем Poster_URL
                            "description": row.get('Description', 'Описание отсутствует'),
                            "year": row.get('Year', 'Не указан'),
                            "Score": row.get('Score', 'Не указан')
                            
                        }
                        movies.append(movie_data)
    except FileNotFoundError:
        pass
    except Exception as e:
        pass

    return movies


def get_random_movies(movies, n=3):
    return random.sample(movies, min(n, len(movies)))
