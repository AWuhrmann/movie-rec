from asyncio.log import logger
from typing import List
from app.models.recommendation import AlgorithmType, Rating, MovieRecommendation, JobStatus
from app.services.job_stores import JobStore
import pandas as pd
import numpy as np
import scipy
from sklearn.neighbors import NearestNeighbors
from fastapi import FastAPI
import os

ratings_sparse = None
data_folder = './app/'
#paths to files
movie_metadata_path = data_folder + 'movie.metadata.tsv'

df = None
movie_mapping = None
user_mapping = None
sparse_matrix_rep = None

app = FastAPI()

def formating_imdbId(x) :
    x= round(x)
    x_str= str(x)
    while len(x_str) < 7 :
        x_str= '0' + x_str
    return 'tt' + x_str

def generate_sparse_vector_from_ratings(list_of_imdbid_and_rating, total_nbr_of_movies) :
    small_df= pd.DataFrame(data= list_of_imdbid_and_rating, columns= ['imdbId', 'rating'])
    ratings= np.array(small_df['rating'].values, dtype= float) - 2.25
    movie_ids= small_df['imdbId'].map(movie_mapping).values
    imdb_ids= small_df['imdbId']
    return scipy.sparse.csr_matrix((ratings, (np.zeros(len(movie_ids)), movie_ids)), shape= (1, total_nbr_of_movies)), imdb_ids

def weighted_rating(R, v, m, C):
    # Calculation based on the IMDB formula
    return (v/(v+m) * R) + (m/(m+v) * C)

def inverse_imdb_transform(imdb):
    return int(imdb[2:])

def recommand_movies_for_website_user(ratings: List[Rating], n_neighbors=2, n_movies= 2) :
    global merged_df, df_more_reduced, sparse_matrix_rep

    list_= [[inverse_imdb_transform(rating.imdb_id), rating.rating] for rating in ratings]

    print(list_)

    total_nbr_of_movies= sparse_matrix_rep.shape[1]
    sparse_vec, movies_watched= generate_sparse_vector_from_ratings(list_, total_nbr_of_movies)
    # Generate a fit to approximate nearest neighbors of a given user in the database
    knn_function= NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=n_neighbors, n_jobs=-1)
    knn_function.fit(sparse_matrix_rep)
    distances, indices= knn_function.kneighbors(sparse_vec, n_neighbors= n_neighbors)
    indices= indices[0, :]
    moviesid_to_check= df[df['new_userId'].isin(indices)]
    df_temp= moviesid_to_check.groupby('imdbId')
    averages= df_temp['rating'].mean()
    C= averages.mean()
    number_of_votes= df_temp['new_userId'].count()
    m= number_of_votes.quantile(0.8)
    scores= weighted_rating(averages, number_of_votes, m , C)
    sorted_scores_id= pd.DataFrame(data= scores.sort_values(ascending= False).index, columns= ['imdbId'])
    final_recommandation= []
    n_temp= n_movies
    while len(final_recommandation) < n_movies :
        movies_recommanded= sorted_scores_id['imdbId'].values[:n_temp]
        final_recommandation= list(set(movies_recommanded) - set(movies_recommanded).intersection(set(movies_watched.values)))
        n_temp+=1
    final_rec_df= pd.DataFrame(data= final_recommandation[:n_movies], columns= ['imdbId'])

    print(final_rec_df['imdbId'].apply(formating_imdbId).values)

    return final_rec_df['imdbId'].apply(formating_imdbId).values

def init_data(app):
    @app.on_event("startup")
    async def load_datasets():
        global user_mapping, movie_mapping, df, sparse_matrix_rep
        # Load datasets once when the server starts
        
        print(os.getcwd())
    
        data_folder = './Data/'
        #paths to files
        file_path = data_folder + 'df_filtered.csv'

        # load the data
        df= pd.read_csv(file_path, index_col=0)
        # Dropping this column because hopefully the final dataframe of ratings in the project won't have it
        df.drop('movieId', axis=1, inplace=True)

        # Generate unique new IDs for movies globally
        movie_mapping = {old_id: new_id for new_id, old_id in enumerate(df['imdbId'].unique(), start=0)}

        # Add the new_movieId column using the global mapping
        df['new_movieId'] = df['imdbId'].map(movie_mapping)

        # Generate unique new IDs for user globally
        user_mapping = {old_id: new_id for new_id, old_id in enumerate(df['userId'].unique(), start=0)}

        # Add the new_userId column using the global mapping
        df['new_userId'] = df['userId'].map(user_mapping)
    
        sparse_matrix_rep= scipy.sparse.load_npz("./Data/Sparse_hyperspace_user_movie.npz")

def content_based_filtering(ratings: List[Rating]) -> List[MovieRecommendation]:
    recommendations = ["tt0073195", "tt0078788"]
    
    return recommendations

def hybrid_recommendations(ratings: List[Rating]) -> List[MovieRecommendation]:
    recommendations = ["tt0083658", "tt0033467"]
    
    return recommendations

async def generate_recommendations(job_id: str, ratings: List[Rating], algorithm: AlgorithmType):
    try:
        recommendations = []
        if algorithm == AlgorithmType.COLLABORATIVE:
            recommendations = recommand_movies_for_website_user(ratings)
        elif algorithm == AlgorithmType.CONTENT_BASED:
            recommendations = content_based_filtering(ratings)
        elif algorithm == AlgorithmType.HYBRID:
            recommendations = hybrid_recommendations(ratings)
        
        JobStore.update_job(
            job_id,
            JobStatus(status="completed", results=recommendations)
        )
    except Exception as e:
        JobStore.update_job(
            job_id,
            JobStatus(status="failed", error=str(e))
        )