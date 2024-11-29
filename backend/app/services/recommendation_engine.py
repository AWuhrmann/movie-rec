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

merged_df = None
df_more_reduced = None
sparse_matrix_rep = None

app = FastAPI()

# load the data
# Function that generate a sparse vector of the hyperspace user-movies from the ratings and movie-ids given by the website user
def generate_sparse_vector_from_ratings(list_of_imdbid_and_rating, total_nbr_of_movies) :
    global merged_df, df_more_reduced
    
    print('bonjour')


    bidule= np.array(list_of_imdbid_and_rating)

    imdb_ids= bidule[:, 0]
    ratings= np.array(bidule[:, 1], dtype= float)

    movie_ids= merged_df[merged_df['imdbId_str'].isin(imdb_ids)]['movieId'].values
    
    movie_ids= movie_ids - 1

    print('ratings:', ratings)
    print('movie_ids:', movie_ids)
    print('total_nbr_of_movies:', total_nbr_of_movies)

    test = scipy.sparse.csr_matrix((ratings, (np.zeros(len(movie_ids)), movie_ids)), shape= (1, total_nbr_of_movies)), movie_ids + 1

    print('sdfhkj')

    return scipy.sparse.csr_matrix((ratings, (np.zeros(len(movie_ids)), movie_ids)), shape= (1, total_nbr_of_movies)), movie_ids + 1
def weighted_rating(R, v, m, C):
    # Calculation based on the IMDB formula
    return (v/(v+m) * R) + (m/(m+v) * C)

def recommand_movies_for_website_user(ratings: List[Rating], n_neighbors=30, n_movies= 5) :
    global merged_df, df_more_reduced, sparse_matrix_rep

    list_= [[rating.imdb_id, rating.rating] for rating in ratings]

    print(list_)

    total_nbr_of_movies= sparse_matrix_rep.shape[1]
    sparse_vec, movies_watched_id= generate_sparse_vector_from_ratings(list_, total_nbr_of_movies)
    # Generate a fit to approximate nearest neighbors of a given user in the database
    
    knn_function= NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=n_neighbors, n_jobs=-1)
    knn_function.fit(sparse_matrix_rep)
    
    print('hello world x4')
    distances, indices= knn_function.kneighbors(sparse_vec, n_neighbors= n_neighbors)
    indices= indices[0, 1:] + 1
    moviesid_to_check= df_more_reduced[(df_more_reduced['userId'].isin(indices)) & (df_more_reduced['rating']>= 0)]
    df_temp= moviesid_to_check.groupby('movieId')
    averages= df_temp['rating'].mean()
    C= averages.mean()
    number_of_votes= df_temp['userId'].count()
    m= number_of_votes.quantile(0.8)
    print('hello world x5')
    scores= weighted_rating(averages, number_of_votes, m , C)
    sorted_scores_id= scores.sort_values(ascending= False).index
    movies_watched=  merged_df[merged_df['movieId'].isin(movies_watched_id)]['movie_name_formatted']
    print(movies_watched)
    print('hello world x6')
    final_recommandation= []
    n_temp= n_movies

    while len(final_recommandation) < n_movies :
        movies_recommanded= merged_df[merged_df['movieId'].isin(sorted_scores_id[:n_temp])]['movie_name_formatted']
        final_recommandation= list(set(movies_recommanded.values) - set(movies_recommanded.values).intersection(set(movies_watched.values)))
        n_temp+=1

    recommendations = merged_df[merged_df['movie_name_formatted'].isin(final_recommandation)][['movie_name', 'imdbId_str']]
    recommendations = recommendations.drop_duplicates(subset='imdbId_str')[:n_movies]

    recommendations = [MovieRecommendation(id=movie.imdbId_str, title=movie.movie_name) for movie in recommendations.itertuples()]    

    print(recommendations)

    return recommendations
    

def init_data(app):
    @app.on_event("startup")
    async def load_datasets():
        global merged_df, df_more_reduced, sparse_matrix_rep
        # Load datasets once when the server starts
        
        print(os.getcwd())
        
        movie_metadata_df = pd.read_csv(movie_metadata_path, delimiter='\t', names=['wikipedia_movie_id', 'freebase_movie_id', 
                                                                                'movie_name', 'release_date', 'box_office_revenue',
                                                                                'runtime', 'languages', 'countries', 'genres'], 
                                    encoding='utf-8')



        df = pd.read_csv('./app/ratings.csv')

        movies = pd.read_csv('app/movies.csv')
        # Formatting the movie names in the two database such that they can latter be merged on the names
        movie_metadata_df['movie_name_formatted'] = movie_metadata_df['movie_name'].str.lower().str.strip()
        movies['title_format'] = movies['title'].str[:-6].str.strip().str.lower()
        # calculate the number of common movies between the two datasets

        common_movies = set(movie_metadata_df['movie_name_formatted']).intersection(set(movies['title_format']))
        print('Number of common movies:', len(common_movies))

        # merge the two datasets
        links = pd.read_csv('app/links.csv')
        merged_df = pd.merge(movies, movie_metadata_df, left_on='title_format', right_on='movie_name_formatted', how='inner')

        merged_df = pd.merge(merged_df, links, left_on='movieId', right_on='movieId', how='inner')

        def rename_with_tt(id):
            return 'tt' + ''.join(['0'] * (7 - len(str(id)))) + str(id)

        merged_df['imdbId_str'] = merged_df['imdbId'].apply(rename_with_tt) 

        merged_df.head()
        # Only take common movies for analysis
        movieId_to_keep= set(merged_df[merged_df['movie_name_formatted'].isin(common_movies)]['movieId'])
        df_reduced= df[df['movieId'].isin(movieId_to_keep)]
        print(df_reduced.shape)
        # Number of user is reduced for now otherwise the code won't run because the matrix is too big
        df_more_reduced= df_reduced[df_reduced['userId'] < 80000]
        sparse_matrix_rep = scipy.sparse.load_npz("app/Sparse_hyperspace_user_movie.npz")

    

def collaborative_filtering(ratings: List[Rating]) -> List[MovieRecommendation]:
    
    recommendations = [
            MovieRecommendation(id="tt0111161", title="The Shawshank Redemption"),
            MovieRecommendation(id="tt0068646", title="The Godfather")
        ]
    
    return recommendations
    
def content_based_filtering(ratings: List[Rating]) -> List[MovieRecommendation]:
    recommendations = [
            MovieRecommendation(id="tt0073195", title="Jaws"),
            MovieRecommendation(id="tt0078788", title="Apocalypse Now")
        ]
    
    return recommendations

def hybrid_recommendations(ratings: List[Rating]) -> List[MovieRecommendation]:
    recommendations = [
            MovieRecommendation(id="tt0083658", title="Blade Runner"),
            MovieRecommendation(id="tt0033467", title="Citizen Kane")
        ]
    
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