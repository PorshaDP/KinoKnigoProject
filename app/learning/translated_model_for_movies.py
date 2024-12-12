import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
import numpy as np
import joblib
import os
import nltk

# # Загрузка русских стоп-слов
# nltk.download('stopwords')
# from nltk.corpus import stopwords
#
# russian_stopwords = stopwords.words('russian')

# Пути к файлам
data_path = os.path.join(os.path.dirname(__file__), 'filtered_translated_movies.csv')
model_path = os.path.join(os.path.dirname(__file__), 'recommender_translated_movies.pkl')
vectorizer_path = os.path.join(os.path.dirname(__file__), 'vectorizer_translated_movies.pkl')

# def train_model():
#     try:
#         movies = pd.read_csv(data_path)
#     except FileNotFoundError:
#         return {"error": f"Ошибка: файл {data_path} не найден."}
#
#     required_columns = {'Title', 'Genre', 'Year', 'Score', 'Description'}
#     if not required_columns.issubset(set(movies.columns)):
#         return {"error": f"Датасет должен содержать столбцы: {required_columns}"}
#
#     if os.path.exists(model_path) and os.path.exists(vectorizer_path):
#         return {"message": "Модель и векторизатор уже существуют, обучение не требуется."}
#
#     # Используем русские стоп-слова
#     tfidf = TfidfVectorizer(stop_words=russian_stopwords, max_features=5000)
#     description_vectors = tfidf.fit_transform(movies['Description'])
#
#     scaler = MinMaxScaler()
#     movies['Score_normalized'] = scaler.fit_transform(movies[['Score']])
#
#     movie_features = np.hstack((description_vectors.toarray(), movies['Score_normalized'].values.reshape(-1, 1)))
#
#     knn_model = NearestNeighbors(metric='cosine', algorithm='brute')
#     knn_model.fit(movie_features)
#
#     try:
#         joblib.dump(knn_model, model_path)
#         joblib.dump(tfidf, vectorizer_path)
#         return {"message": "Модель и векторизатор успешно сохранены!"}
#     except Exception as e:
#         return {"error": f"Ошибка при сохранении модели: {e}"}
from stop_words import get_stop_words

# Загружаем список русских стоп-слов
russian_stopwords = get_stop_words('russian')

# Пути к файлам
data_path = os.path.join(os.path.dirname(__file__), 'filtered_translated_movies.csv')
model_path = os.path.join(os.path.dirname(__file__), 'recommender_translated_movies.pkl')
vectorizer_path = os.path.join(os.path.dirname(__file__), 'vectorizer_translated_movies.pkl')

def train_model():
    try:
        movies = pd.read_csv(data_path)
    except FileNotFoundError:
        return {"error": f"Ошибка: файл {data_path} не найден."}

    required_columns = {'Title', 'Genre', 'Year', 'Score', 'Description'}
    if not required_columns.issubset(set(movies.columns)):
        return {"error": f"Датасет должен содержать столбцы: {required_columns}"}

    if os.path.exists(model_path) and os.path.exists(vectorizer_path):
        return {"message": "Модель и векторизатор уже существуют, обучение не требуется."}

    # Используем русские стоп-слова
    tfidf = TfidfVectorizer(stop_words=russian_stopwords, max_features=5000)
    description_vectors = tfidf.fit_transform(movies['Description'])

    scaler = MinMaxScaler()
    movies['Score_normalized'] = scaler.fit_transform(movies[['Score']])

    movie_features = np.hstack((description_vectors.toarray(), movies['Score_normalized'].values.reshape(-1, 1)))

    knn_model = NearestNeighbors(metric='cosine', algorithm='brute')
    knn_model.fit(movie_features)

    try:
        joblib.dump(knn_model, model_path)
        joblib.dump(tfidf, vectorizer_path)
        return {"message": "Модель и векторизатор успешно сохранены!"}
    except Exception as e:
        return {"error": f"Ошибка при сохранении модели: {e}"}
def recommend_movies(movie_title, num_recommendations=10):
    if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
        return {"error": "Модель не обучена, пожалуйста, обучите модель перед использованием"}

    try:
        movies = pd.read_csv(data_path)
        knn_model = joblib.load(model_path)
        tfidf = joblib.load(vectorizer_path)
    except Exception as e:
        return {"error": f"Ошибка при загрузке данных или модели: {e}"}

    scaler = MinMaxScaler()
    movies['Score_normalized'] = scaler.fit_transform(movies[['Score']])

    movie_title_lower = movie_title.lower()

    try:
        movie_index = movies[movies['Title'].str.lower() == movie_title_lower].index[0]
        movie_description = movies.iloc[movie_index]['Description']
        movie_score_normalized = movies.iloc[movie_index]['Score_normalized']

        movie_vector = tfidf.transform([movie_description]).toarray()
        movie_features = np.hstack((movie_vector, np.array([[movie_score_normalized]])))

        distances, indices = knn_model.kneighbors(movie_features, n_neighbors=num_recommendations + 1)

        recommended_movies = movies.iloc[indices[0][1:]]  # Пропускаем сам фильм

        recommendations = recommended_movies[['Title', 'Genre', 'Year', 'Score', 'Description']].to_dict(orient='records')
        return recommendations

    except IndexError:
        return {"error": "Фильм не найден"}
    except Exception as e:
        return {"error": f"Ошибка при обработке запроса: {e}"}

# if __name__ == "__main__":
#     # Тест: обучение модели
#     train_result = train_model()
#     print("Результат обучения модели:")
#     print(train_result)
#
#     # Тестовые данные для рекомендаций
#     test_title = "Зарождение"  # Укажите реальное название фильма из вашего датасета
#     num_recommendations = 5
#
#     # Тест: получение рекомендаций
#     recommend_result = recommend_movies(test_title, num_recommendations)
#     print("\nРекомендации:")
#     print(recommend_result)