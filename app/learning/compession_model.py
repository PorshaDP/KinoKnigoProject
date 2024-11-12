import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import joblib
from pathlib import Path


#project_dir = Path(__file__).resolve().parent.parent  # Путь к корневой папке проекта

# Пути к файлам данных
# movies_path = project_dir / 'learning' / 'movie.csv'
# ratings_path = project_dir / 'learning' / 'rating.csv'
movies = pd.read_csv('/Users/arzu_shakh/Downloads/MovieLens/movie.csv')
ratings = pd.read_csv('/Users/arzu_shakh/Downloads/MovieLens/rating.csv')
# Загрузка данных
# movies = pd.read_csv(movies_path)
# ratings = pd.read_csv(ratings_path)

# Убираем ненужные колонки
movies.drop(['genres'], axis=1, inplace=True)
ratings.drop(['timestamp'], axis=1, inplace=True)

# Строим матрицу пользователь-фильм
user_item_matrix = ratings.pivot(index='movieId', columns='userId', values='rating')
user_item_matrix.fillna(0, inplace=True)

csr_data = csr_matrix(user_item_matrix.values)

# Обучаем модель KNN
knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
knn.fit(csr_data)

# Сохраняем модель и матрицу для дальнейшего использования со сжатием
joblib.dump(knn, 'knn_model_compressed.pkl', compress=3)  # compress=3 — степень сжатия (0-9)
user_item_matrix.to_pickle('user_item_matrix_compress.pkl', compression="gzip")  # Сжимаем саму матрицу

print("Модель и матрица сохранены с сжатием.")