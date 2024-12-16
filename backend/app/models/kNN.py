import heapq
import numpy as np
import pandas as pd
import scipy

def filter_ratings_dataframe(df, k):
    """
    Function that remove users and movies with less than k ratings
    """
    # Remove Users
    review_counts = df.groupby('userId')['rating'].count()
    valid_users = review_counts[review_counts >= k].index
    print(f"Number of valid users: {len(valid_users)}")
    df_filtered = df[df['userId'].isin(valid_users)].copy()

    # Remove Users
    review_counts = df_filtered.groupby('movieId')['rating'].count()
    valid_movies = review_counts[review_counts >= 5].index
    print(f"Number of valid movies: {len(valid_movies)}")
    df_ratings = df_filtered[df_filtered['movieId'].isin(valid_movies)].copy()

    return df_ratings


def optimize_recommendations_for_single_user(
    new_ratings,  # List of (movie_id, rating) tuples
    df_ratings,   # Original ratings DataFrame
    movie_map,    # Mapping of external movie IDs to sparse matrix indices
    knn,          # Fitted K-Nearest Neighbors model
    ratings_matrix,  # Sparse ratings matrix
    num_recommendations=5,
    n_neighbors_to_take=20,
    live=False
):

    # Convert new ratings to sparse vector
    movie_ids = np.array([movie_map[rating[0]] for rating in new_ratings])
    ratings = np.array([rating[1] for rating in new_ratings])
    number_of_movies = ratings_matrix.shape[1]
    global_mean = df_ratings['rating'].mean()

    print(ratings)
    print(movie_ids)
    print(number_of_movies)
    
    # Create sparse vector for the user
    sparse_vector = scipy.sparse.csr_matrix(
        (ratings, (np.zeros_like(movie_ids), movie_ids)),
        shape=(1, number_of_movies)
    )
    
    # Compute distances and indices of neighbors
    distances, neighbor_indices = knn.kneighbors(
        sparse_vector,
        n_neighbors=n_neighbors_to_take,
        return_distance=True
    )
    # print(neighbor_indices)
    # Remove self from neighbors (first index)
    neighbor_indices = neighbor_indices[0, 1:]
    distances = distances[0, 1:]
    
    # Convert distances to weights (inverse of distance)
    # Add small epsilon to avoid division by zero
    weights = 1 - distances
    
    # Create weights dictionary for the neighbor users
    weights_dict = {neighbor_indices[i]: weights[i] for i in range(len(neighbor_indices))}
    
    # Precompute user mean and std ratings
    user_mean_ratings = df_ratings.groupby('sparse_user_id')['rating'].mean()
    user_std_ratings = df_ratings.groupby('sparse_user_id')['rating'].std().fillna(1)
    
    # Precompute movie-user mapping
    movie_users = df_ratings.groupby('sparse_movie_id')['sparse_user_id'].agg(list)
    
    # Compute user's own mean and std of ratings
    r_u = np.mean(ratings)
    std_u = np.std(ratings)
    
    # Prepare results for different recommendation methods
    user_results_mean_centering = []
    user_results_z_normalization = []
    user_results_basic = []
    
    # Exclude movies already rated by the user
    if live:
        all_movies = df_ratings[df_ratings['sparse_user_id'].isin(neighbor_indices)]['sparse_movie_id'].unique()
        print(len(all_movies))
        if len(all_movies) > 100:
            selected_movies = np.random.choice(all_movies, size=100, replace=False)
            all_movies = selected_movies
    else:
        # Get all unique movies in the system
        all_movies = df_ratings['sparse_movie_id'].unique()
    print(f"Number of movies: {len(all_movies)}")
    candidate_movies = [movie for movie in all_movies if movie not in movie_ids]
    
    print('start6')
    for i, movie in enumerate(candidate_movies):
        if i % 100 == 0:
            print(f"{i}/{len(candidate_movies)}")
        # Get movie users list
        movie_users_list = movie_users.get(movie, [])
        #print(movie_users_list)
        # Select top K users efficiently
        top_users = heapq.nlargest(
            30,  # limiting to top 30 users 
            [(uid, weights_dict.get(uid, 0)) for uid in movie_users_list if weights_dict.get(uid, 0) > 0],
            key=lambda x: x[1]
        )
        
        # Filter ratings for top users
        user_ratings = df_ratings[
            (df_ratings['sparse_movie_id'] == movie) & 
            (df_ratings['sparse_user_id'].isin([u[0] for u in top_users]))
        ].copy()

        #print(user_ratings)
        
        if len(user_ratings) < 5:
            user_results_mean_centering.append((movie, global_mean))
            user_results_z_normalization.append((movie, global_mean))
            user_results_basic.append((movie, global_mean))
            continue
        
        # Add columns for calculations
        user_ratings.loc[:, 'user_weight'] = user_ratings['sparse_user_id'].map(dict(top_users))
        user_ratings.loc[:, 'mean_rating'] = user_ratings['sparse_user_id'].map(user_mean_ratings)
        user_ratings.loc[:, 'std_rating'] = user_ratings['sparse_user_id'].map(user_std_ratings)
        user_ratings.loc[:, 'weighted_diff'] = user_ratings['user_weight'] * (user_ratings['rating'] - user_ratings['mean_rating'])

        #print(user_ratings)
        
        # Compute prediction methods
        numerator = user_ratings['weighted_diff'].sum()
        denominator = user_ratings['user_weight'].abs().sum()
        
        numerator2 = (user_ratings['weighted_diff']/user_ratings['std_rating']).sum()
        numerator3 = (user_ratings['user_weight'] * user_ratings['rating']).sum()
        
        if denominator > 0:
            # Mean Centering Method
            result_mean_centering = numerator / denominator + r_u
            
            # Z-Normalization Method
            result_z_normalization = numerator2 * std_u / denominator + r_u
            
            # Basic Weighted Average Method
            result_basic = numerator3 / denominator
                
            user_results_mean_centering.append((movie, result_mean_centering))
            user_results_z_normalization.append((movie, result_z_normalization))
            user_results_basic.append((movie, result_basic))
    
    # Sort and get top recommendations for each method
    recommendations = {
        'basic': sorted(user_results_basic, key=lambda x: x[1], reverse=True)[:num_recommendations],
        'mean_centering': sorted(user_results_mean_centering, key=lambda x: x[1], reverse=True)[:num_recommendations],
        'z_normalization': sorted(user_results_z_normalization, key=lambda x: x[1], reverse=True)[:num_recommendations]
    }
    

    return recommendations