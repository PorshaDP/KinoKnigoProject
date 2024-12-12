import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
import numpy as np
import joblib
import os
from stop_words import get_stop_words

# Пути к файлам
data_path = os.path.join(os.path.dirname(__file__), 'filtered_translated_books.csv')
model_path = os.path.join(os.path.dirname(__file__), 'recommender_translated_books.pkl')
vectorizer_path = os.path.join(os.path.dirname(__file__), 'vectorizer_translated_books.pkl')

# Функция обучения модели
def train_model():
    try:
        books = pd.read_csv(data_path)
    except FileNotFoundError:
        return {"error": f"Ошибка: файл {data_path} не найден."}

    required_columns = {'title', 'authors', 'published_year', 'categories', 'description', 'average_rating', 'num_pages'}
    if not required_columns.issubset(set(books.columns)):
        return {"error": f"Датасет должен содержать столбцы: {required_columns}"}

    if os.path.exists(model_path) and os.path.exists(vectorizer_path):
        return {"message": "Модель и векторизатор уже существуют, обучение не требуется."}

    # Загружаем список русских стоп-слов
    russian_stopwords = get_stop_words('russian')

    # Векторизация описаний книг
    tfidf = TfidfVectorizer(stop_words=russian_stopwords, max_features=5000)
    description_vectors = tfidf.fit_transform(books['description'])

    # Нормализация рейтингов
    scaler = MinMaxScaler()
    books['average_rating_normalized'] = scaler.fit_transform(books[['average_rating']])

    # Создание комбинированных признаков
    book_features = np.hstack((description_vectors.toarray(), books['average_rating_normalized'].values.reshape(-1, 1)))

    # Обучение модели KNN
    knn_model = NearestNeighbors(metric='cosine', algorithm='brute')
    knn_model.fit(book_features)

    try:
        # Сохранение модели и векторизатора
        joblib.dump(knn_model, model_path)
        joblib.dump(tfidf, vectorizer_path)
        return {"message": "Модель и векторизатор успешно сохранены!"}
    except Exception as e:
        return {"error": f"Ошибка при сохранении модели: {e}"}

# Функция для получения рекомендаций
def recommend_books(book_title, num_recommendations=10):
    if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
        return {"error": "Модель не обучена, пожалуйста, обучите модель перед использованием"}

    try:
        books = pd.read_csv(data_path)
        knn_model = joblib.load(model_path)
        tfidf = joblib.load(vectorizer_path)
    except Exception as e:
        return {"error": f"Ошибка при загрузке данных или модели: {e}"}

    scaler = MinMaxScaler()
    books['average_rating_normalized'] = scaler.fit_transform(books[['average_rating']])

    book_title_lower = book_title.lower()

    try:
        # Поиск книги
        book_index = books[books['title'].str.lower() == book_title_lower].index[0]
        book_description = books.iloc[book_index]['description']
        book_rating_normalized = books.iloc[book_index]['average_rating_normalized']

        # Создание вектора книги
        book_vector = tfidf.transform([book_description]).toarray()
        book_features = np.hstack((book_vector, np.array([[book_rating_normalized]])))

        # Поиск ближайших соседей
        distances, indices = knn_model.kneighbors(book_features, n_neighbors=num_recommendations + 1)

        # Пропуск самой книги
        recommended_books = books.iloc[indices[0][1:]]

        recommendations = recommended_books[['title', 'authors', 'categories', 'published_year', 'average_rating', 'description', 'thumbnail']].to_dict(orient='records')
        return recommendations

    except IndexError:
        return {"error": "Книга не найдена"}
    except Exception as e:
        return {"error": f"Ошибка при обработке запроса: {e}"}

# Пример запуска
if __name__ == "__main__":
    result = train_model()
    if 'error' in result:
        print(result['error'])
    else:
        print(result['message'])

    book_title = input("Введите название книги для рекомендаций: ")
    recommendations = recommend_books(book_title, num_recommendations=5)

    if "error" in recommendations:
        print(f"Ошибка: {recommendations['error']}")
    else:
        for book in recommendations:
            print(f"Название: {book['title']}, Автор: {book['authors']}, Категории: {book['categories']}")
            print(f"Год публикации: {book['published_year']}, Рейтинг: {book['average_rating']}")
            print(f"Описание: {book['description']}")
            print(f"Картинка: {book['thumbnail']}\n")