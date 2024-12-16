from asyncio.log import logger
from typing import List
from app.models.recommendation import AlgorithmType, Rating, MovieRecommendation, JobStatus
from app.services.job_stores import JobStore
import pandas as pd
import numpy as np
import scipy
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
from app.models.SparseSVDRecommender import SparseSVDRecommender
from fastapi import FastAPI
import os
from thefuzz import fuzz, process
from app.models.kNN import *
from sklearn.neighbors import NearestNeighbors


ratings_sparse = None
data_folder = './app/'
#paths to files
movie_metadata_path = data_folder + 'movie.metadata.tsv'

df = None
movie_mapping = None
reverse_movie_mapping = None
user_mapping = None
sparse_matrix = None
movie_names = None
recommender = None
df_ratings = None
knn = NearestNeighbors(metric='cosine', algorithm='brute', n_jobs=-1, n_neighbors=20)

encodings, movie_mapping_SAE, reverse_movie_mapping_SAE = None, None, None

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



def init_data(app):
    @app.on_event("startup")
    async def load_datasets():
        global user_mapping, movie_mapping, df_ratings, sparse_matrix, movie_names, recommender, reverse_movie_mapping, knn
        # Load datasets once when the server starts
        
        logger.info(os.getcwd())
        movie_names = pd.read_csv('./Data/movie_names.csv', index_col=0)

        # load the data
        
        logger.info('Loading ratings')
        df_ratings = pd.read_csv('./Data/df_ratings_knn.csv', index_col=0)
        logger.info('Loading sparse matrix')
        sparse_matrix = scipy.sparse.load_npz("./Data/sparse_ratings_matrix.npz")
        
        logger.info('Fitting kNN to sparse')
        knn.fit(sparse_matrix)
        
        movie_mapping = np.load('./Data/movie_mapping.npy', allow_pickle=True).item()
        reverse_movie_mapping = np.load('./Data/reverse_movie_mapping.npy', allow_pickle=True).item()

    

        # ------------------------------ SVD ------------------------------------ # 

        logger.info('Loading SparseSVD')
        recommender = SparseSVDRecommender()
    
        logger.info('Loading model for SVD')
        recommender.load_model('Data/sample_svd_model14.joblib')

        # -------------------------------- CONTENT BASED ------------------------  #
        global encodings, movie_mapping_SAE, reverse_movie_mapping_SAE

        logger.info('Loading Content based values')

        encodings = np.load('./Data/SAE_embedding.npy', allow_pickle=True)
        movie_mapping_SAE = np.load('./Data/mapping_SAE.npy', allow_pickle=True).item()
        reverse_movie_mapping_SAE = np.load('./Data/reverse_mapping_SAE.npy', allow_pickle=True).item()

# ------------------------------------------ ALGO ------------------------------------------------

def recommend_SAE(ratings: List[Rating]):
    
    imdbid = [inverse_imdb_transform(rating.imdb_id) for rating in ratings]

    similarities = np.zeros(encodings.shape[0])
    for movie in imdbid:

        id = movie_mapping_SAE[movie]

        embedding = encodings[id].reshape(1,-1)

        similarities += cosine_similarity(encodings, embedding).ravel()

        similarities[id] = float('-inf')

    similar_indices = np.argsort(similarities)[::-1]
    print(similar_indices[:5])
    recommendations = [formating_imdbId(reverse_movie_mapping_SAE[rec_id]) for rec_id in similar_indices[:5]]
    
    results = [MovieRecommendation(id=id, title=movie_names[movie_names['imdb_id'] == id]['title'].values[0]) for id in recommendations]

    print(f'SVD Result : {results}')

    return results



def recommend_kNN(ratings: List[Rating]):
    
    list_= [[str(inverse_imdb_transform(rating.imdb_id)), rating.rating] for rating in ratings]
    
    recommendations = optimize_recommendations_for_single_user(
        list_,  # List of (movie_id, rating) tuples
        df_ratings,   # Original ratings DataFrame
        movie_mapping,    # Mapping of external movie IDs to sparse matrix indices
        knn,          # Fitted K-Nearest Neighbors model
        sparse_matrix,  # Sparse ratings matrix
        num_recommendations=5,
        n_neighbors_to_take=20,
        live=True)

    recommendations = recommendations['mean_centering']
    imdb_id = [formating_imdbId(int(reverse_movie_mapping[rec[0]])) for rec in recommendations]

    results = [MovieRecommendation(id=id, title=movie_names[movie_names['imdb_id'] == id]['title'].values[0]) for id in imdb_id]

    return results

def SVD_recommendation(ratings: List[Rating]):
    
    ratings = [[str(inverse_imdb_transform(rating.imdb_id)), rating.rating] for rating in ratings]

    new_ratings_df = pd.DataFrame(ratings, columns=['original_movie_id', 'rating'])
    new_ratings_df['original_movie_id'] = new_ratings_df['original_movie_id']

    new_ratings_df['sparse_movie_id'] = new_ratings_df['original_movie_id'].map(movie_mapping)
    ratings_to_pass_df = new_ratings_df.drop(columns=['original_movie_id'])

    recommendations = recommender.handle_new_user(ratings_to_pass_df, n_items=5)

    ids = [formating_imdbId(int(reverse_movie_mapping[rec[0]])) for rec in recommendations[:5]]

    results = [MovieRecommendation(id=id, title=movie_names[movie_names['imdb_id'] == id]['title'].values[0]) for id in ids]

    print(f'SVD Result : {results}')

    return results


def content_based_filtering(ratings: List[Rating]) -> List[MovieRecommendation]:
    recommendations = ["tt0073195", "tt0078788"]
    
    return recommendations

def hybrid_recommendations(ratings: List[Rating]) -> List[MovieRecommendation]:
    recommendations = ["tt0083658", "tt0033467"]
    
    return recommendations


async def check_if_in(job_id: str, movies: List[str]):
    try:
        isIn = []
        for movie in movies:
            if movie in movie_mapping:
                isIn.append(movie)
    except Exception as e:
        JobStore.update_job(job_id, 
                            JobStatus('failed', error=str(e)))

async def find_movie(query: str, threshold):
    try:
        print('Start job', query, type(query))
        choices = movie_names['title'] # dict(zip(movie_names['title'], df.index))
        print(f'Got choices', list(choices.items())[:10])
        matches = process.extractBests(
            query,
            choices,
            limit=10,
        )
        print('Extracted best matches', matches)

        if not matches:
            results = []
        else:
            matched_indices = [match[2] for match in matches]
            result_df = movie_names.loc[matched_indices].copy()
            result_df['similarity_score'] = [match[1] for match in matches]
            results = result_df.sort_values('similarity_score', ascending=False)
        
        print(results)
        
        return [{"title": row.title, "imdb_id": row.imdb_id} for row in results.itertuples()]

    except Exception as e:
        print(e)
        return []


async def generate_recommendations(job_id: str, ratings: List[Rating], algorithm: AlgorithmType):
    try:
        recommendations = []
        if algorithm == AlgorithmType.COLLABORATIVE:
            recommendations = recommend_kNN(ratings)
        elif algorithm == AlgorithmType.CONTENT_BASED:
            recommendations = recommend_SAE(ratings)
        elif algorithm == AlgorithmType.HYBRID:
            recommendations = hybrid_recommendations(ratings)
        elif algorithm == AlgorithmType.SVD:
            print('start svd')
            recommendations = SVD_recommendation(ratings)

        JobStore.update_job(
            job_id,
            JobStatus(status="completed", results=recommendations)
        )
    except Exception as e:
        print(e)
        JobStore.update_job(
            job_id,
            JobStatus(status="failed", error=str(e))
        )