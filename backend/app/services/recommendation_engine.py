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

from app.models.collaborative import *

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
knn_user = NearestNeighbors(metric='cosine', algorithm='brute', n_jobs=-1, n_neighbors=20)
knn_item = NearestNeighbors(metric='cosine', algorithm='brute', n_jobs=-1, n_neighbors=20)


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
        global user_mapping, movie_mapping, df_ratings, sparse_matrix, movie_names, recommender, reverse_movie_mapping, knn_user
        # Load datasets once when the server starts
        
        logger.info(os.getcwd())
        movie_names = pd.read_csv('./Data/movie_names_dates_imdb.csv', index_col=0)

        # load the data
        
        logger.info('Loading ratings')
        df_ratings = pd.read_csv('./Data/df_ratings_knn.csv', index_col=0)
        logger.info('Loading sparse matrix')
        sparse_matrix = scipy.sparse.load_npz("./Data/sparse_ratings_matrix.npz")
        
        logger.info('Fitting kNN to sparse user')
        knn_user.fit(sparse_matrix) 
        
        logger.info('Fitting kNN to sparse item')
        knn_item.fit(sparse_matrix.T) 
        
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

def get_rec_from_ids(imdb_ids: List[str]):

    return [MovieRecommendation(id=id, 
                                title=movie_names[movie_names['imdb_id'] == id]['title'].values[0],
                                year=movie_names[movie_names['imdb_id'] == id]['year'].values[0] 
                                    if movie_names[movie_names['imdb_id'] == id]['year'].values[0] > 0 
                                    else None
                                    ) for id in imdb_ids]


def recommend_SAE(ratings: List[Rating], fixed_count, min_similarity=0):
    
    imdbid = [inverse_imdb_transform(rating.imdb_id) for rating in ratings]

    similarities = np.zeros(encodings.shape[0])
    for movie in imdbid:

        id = movie_mapping_SAE[movie]

        embedding = encodings[id].reshape(1,-1)

        similarities += cosine_similarity(encodings, embedding).ravel()

        similarities[id] = float('-inf')


    if min_similarity > 0:
        similarities[similarities < min_similarity] = float('-inf')
            
    # Get top N recommendations
    similar_indices = np.argsort(similarities)[::-1][:fixed_count]
    
    # Convert back to IMDb IDs
    recommendations = [
        formating_imdbId(reverse_movie_mapping_SAE[rec_idx])
        for rec_idx in similar_indices
        if similarities[rec_idx] != float('-inf')
    ]
    print(recommendations)
    results = get_rec_from_ids(recommendations)    
    print(results)

    return results


async def recommend_kNN_item_based(ratings: List[Rating], fixed_count, k, minCommonItems, jobid=None):

    try:
        # Update status to running
        await JobStore.update_job(jobid, JobStatus(status="running"))
        
        # Run CPU-intensive operations in a thread
        loop = asyncio.get_event_loop()
        
        # Wrap your CPU-intensive operations in a function
        def compute_recommendations():
            print('testtt1')
            means_by_movie = df_ratings.groupby('sparse_movie_id')['rating'].mean()
            print('testtt2')
            std_by_movie = df_ratings.groupby('sparse_movie_id')['rating'].std()
            ratings_new_user = [[str(inverse_imdb_transform(rating.imdb_id)), rating.rating] for rating in ratings]
            print('testtt3')
            knn_item = NearestNeighbors(metric='cosine', algorithm='brute', n_jobs=-1, n_neighbors=k)
            knn_item.fit(sparse_matrix.T)
            return means_by_movie, std_by_movie, ratings_new_user, knn_item

        # Run CPU-intensive part in thread
        means_by_movie, std_by_movie, ratings_new_user, knn_item = await loop.run_in_executor(
            None,
            compute_recommendations
        )

        # Now run your async function
        recommendations, _ = await reco_item_based_new_user(
            ratings_new_user,
            movie_mapping,
            knn_item,
            means_by_movie,
            std_by_movie,
            sparse_matrix,
            number_of_reco=5,
            number_of_movies_for_reco=minCommonItems,
            jobid=jobid
        )

        print('testtt4')
        
        # Process results in thread if needed
        def process_results():
            imdb_ids = [formating_imdbId(int(reverse_movie_mapping[rec[0]])) for rec in recommendations[:fixed_count]]
            print(imdb_ids)
            return get_rec_from_ids(imdb_ids)

        results = await loop.run_in_executor(None, process_results)
        
        # Update job status with results
        await JobStore.update_job(jobid, JobStatus(status="completed", result=results))
        
        return results
    except Exception as e:
        logger.exception("Error in generate_recommendations")
        await JobStore.update_job(jobid, JobStatus(status="failed", error=str(e)))
        raise



def recommend_kNN_user_based(ratings: List[Rating], fixed_count, k, minCommonUsers, maxMovies):
    
    ratings_new_user = [[str(inverse_imdb_transform(rating.imdb_id)), rating.rating] for rating in ratings]
    
    means_by_user = df_ratings.groupby('sparse_user_id')['rating'].mean()
    std_by_user = df_ratings.groupby('sparse_user_id')['rating'].std()

    recommendations = reco_user_based_new_user(
        ratings_new_user,
        movie_mapping,
        df_ratings,
        knn_user,
        means_by_user,
        std_by_user,
        sparse_matrix.shape[1],
        num_reco=10,
        number_of_neighbors=k,
        max_number_of_movies=maxMovies,
        number_of_users=minCommonUsers)


    recommendations = recommendations['mean_centering'][:fixed_count]
    imdb_ids = [formating_imdbId(int(reverse_movie_mapping[rec[0]])) for rec in recommendations]

    results = get_rec_from_ids(imdb_ids)

    return results

def SVD_recommendation(ratings: List[Rating], fixed_count):
    
    ratings = [[str(inverse_imdb_transform(rating.imdb_id)), rating.rating] for rating in ratings]

    new_ratings_df = pd.DataFrame(ratings, columns=['original_movie_id', 'rating'])
    new_ratings_df['original_movie_id'] = new_ratings_df['original_movie_id']

    new_ratings_df['sparse_movie_id'] = new_ratings_df['original_movie_id'].map(movie_mapping)
    ratings_to_pass_df = new_ratings_df.drop(columns=['original_movie_id'])

    recommendations = recommender.handle_new_user(ratings_to_pass_df, n_items=fixed_count)

    imdb_ids = [formating_imdbId(int(reverse_movie_mapping[rec[0]])) for rec in recommendations[:fixed_count]]

    results = get_rec_from_ids(imdb_ids)

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
        await JobStore.update_job(job_id, 
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
        
        return [{"title": row.title, "imdb_id": row.imdb_id, "year": row.year} for row in results.itertuples()]

    except Exception as e:
        print(e)
        return []


async def generate_recommendations(job_id: str, ratings: List[Rating], algorithm: AlgorithmType, params):
    try:
        print(params)
        fixed_count = 5
        if 'fixedReturns' in params:
            fixed_count = params['fixedReturns']

        recommendations = []
        if algorithm == AlgorithmType.KNN_USER:
            k = 100
            minCommonUsers = 30
            moviesToConsider = 100
            if 'k' in params:
                k = params['k']
            if 'minCommonUsers' in params:
                minCommonUsers = params['minCommonUsers']
            if 'moviesToConsider' in params:
                moviesToConsider = params['moviesToConsider']

            recommendations = recommend_kNN_user_based(ratings, fixed_count, k, minCommonUsers, moviesToConsider)
        
        elif algorithm == AlgorithmType.KNN_ITEM:
            k = 100
            minCommonItems = 30
            if 'k' in params:
                k = params['k']
            if 'minCommonItems' in params:
                minCommonItems = params['minCommonItems']


            recommendations = await recommend_kNN_item_based(ratings, fixed_count, k, minCommonItems, jobid=job_id)
        
        elif algorithm == AlgorithmType.CONTENT_BASED:
            min_similarity = 100
            if 'minSimilarity' in params:
                min_similarity = params['minSimilarity']

            recommendations = recommend_SAE(ratings, fixed_count, min_similarity)
        
        elif algorithm == AlgorithmType.SVD:
            print('start svd')
            recommendations = SVD_recommendation(ratings, fixed_count)

        await JobStore.update_job(
            job_id,
            JobStatus(status="completed", results=recommendations)
        )
    except Exception as e:
        print(e)
        await JobStore.update_job(
            job_id,
            JobStatus(status="failed", error=str(e))
        )