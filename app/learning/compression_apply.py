import pandas as pd
import joblib  # joblib вместо pickle

# Загрузка модели с использованием joblib
knn = joblib.load('knn_model_compressed.pkl')

# Загрузка сжатой матрицы
user_item_matrix = pd.read_pickle('user_item_matrix_compress.pkl', compression="gzip")

movies = pd.read_csv('/Users/arzu_shakh/Downloads/MovieLens/movie.csv')

recommendation = 10

search_word = input('Введите название фильма на англ: ')
movie_search = movies[movies['title'].str.contains(search_word, case=False)]

if not movie_search.empty:
    movie_id = movie_search.iloc[0]['movieId']
    # Найдем индекс фильма в матрице user_item_matrix по индексу movieId
    if movie_id in user_item_matrix.index:
        movie_index = user_item_matrix.index.get_loc(movie_id)

        # Ищем похожие фильмы
        distances, indices = knn.kneighbors(user_item_matrix.iloc[movie_index, :].values.reshape(1, -1),
                                            n_neighbors=recommendation + 1)

        indices_list = indices.squeeze().tolist()
        distances_list = distances.squeeze().tolist()

        # Формируем список рекомендаций
        indices_distance = list(zip(indices_list, distances_list))
        indices_distance_sorted = sorted(indices_distance, key=lambda x: x[1], reverse=True)
        indices_distance_sorted = indices_distance_sorted[:-1]

        recomend_list = []
        for ind_dist in indices_distance_sorted:
            matrix_movie_id = user_item_matrix.index[ind_dist[0]]
            id = movies[movies['movieId'] == matrix_movie_id].index
            title = movies.iloc[id]['title'].values[0]
            dist = ind_dist[1]
            recomend_list.append({'Title': title, 'Match': dist * 100})

        recommend_df = pd.DataFrame(recomend_list, index=range(1, recommendation + 1))
        print(recommend_df)
    else:
        print("Фильм с таким ID не найден в матрице.")
else:
    print("Фильм не найден.")