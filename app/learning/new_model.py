# import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.preprocessing import MinMaxScaler
# from sklearn.neighbors import NearestNeighbors
# import numpy as np
# import joblib
# import os
#
# # Путь к файлам
# # data_path = '/Users/arzu_shakh/PycharmProjects/KinoKnigoProject/app/learning/filtered_movies.csv'
# # model_path = '/Users/arzu_shakh/PycharmProjects/KinoKnigoProject/app/learning/recommender.pkl'
# # vectorizer_path = '/Users/arzu_shakh/PycharmProjects/KinoKnigoProject/app/learning/vectorizer.pkl'
# data_path = os.path.join(os.path.dirname(__file__), 'filtered_movies.csv')
# model_path = os.path.join(os.path.dirname(__file__), 'recommender.pkl')
# vectorizer_path = os.path.join(os.path.dirname(__file__), 'vectorizer.pkl')
#
# # Функция обучения модели
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
#     tfidf = TfidfVectorizer(stop_words='english', max_features=5000)
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
#
#
# # Функция для получения рекомендаций
# def recommend_movies(movie_title, num_recommendations=10):
#     if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
#         return {"error": "Модель не обучена, пожалуйста, обучите модель перед использованием"}
#
#     try:
#         movies = pd.read_csv(data_path)
#         knn_model = joblib.load(model_path)
#         tfidf = joblib.load(vectorizer_path)
#     except Exception as e:
#         return {"error": f"Ошибка при загрузке данных или модели: {e}"}
#
#     scaler = MinMaxScaler()
#     movies['Score_normalized'] = scaler.fit_transform(movies[['Score']])
#
#     movie_title_lower = movie_title.lower()
#
#     try:
#         movie_index = movies[movies['Title'].str.lower() == movie_title_lower].index[0]
#
#         movie_description = movies.iloc[movie_index]['Description']
#         movie_score_normalized = movies.iloc[movie_index]['Score_normalized']
#
#         movie_vector = tfidf.transform([movie_description]).toarray()
#
#         movie_features = np.hstack((movie_vector, np.array([[movie_score_normalized]])))
#
#         distances, indices = knn_model.kneighbors(movie_features, n_neighbors=num_recommendations + 1)
#
#         recommended_movies = movies.iloc[indices[0][1:]]
#
#         print(f"Рекомендации для фильма: {movie_title}")
#         for idx, row in recommended_movies.iterrows():
#             print(f"Название: {row['Title']}, Жанр: {row['Genre']}, Год: {row['Year']}, Оценка: {row['Score']}")
#             print(f"Описание: {row['Description']}\n")
#
#         return recommended_movies[['Title', 'Genre', 'Year', 'Score', 'Description']].to_dict(orient='records')
#
#     except IndexError:
#         return {"error": "Фильм не найден"}
#     except Exception as e:
#         return {"error": f"Ошибка при обработке запроса: {e}"}
#
#
# # Пример запуска
# if __name__ == "__main__":
#     result = train_model()
#     if 'error' in result:
#         print(result['error'])
#     else:
#         print(result['message'])
#
#     movie_title = input("Введите название фильма для рекомендаций: ")
#     recommendations = recommend_movies(movie_title, num_recommendations=5)
#
#     if "error" in recommendations:
#         print(f"Ошибка: {recommendations['error']}")
#     else:
#         for movie in recommendations:
#             print(f"Название: {movie['Title']}, Жанр: {movie['Genre']}, Год: {movie['Year']}, Оценка: {movie['Score']}")
#             print(f"Описание:ф {movie['Description']}\n")


# model.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
import numpy as np
import joblib
import os

# Пути к файлам
data_path = os.path.join(os.path.dirname(__file__), 'filtered_movies.csv')
model_path = os.path.join(os.path.dirname(__file__), 'recommender.pkl')
vectorizer_path = os.path.join(os.path.dirname(__file__), 'vectorizer.pkl')

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

    tfidf = TfidfVectorizer(stop_words='english', max_features=5000)
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