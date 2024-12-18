// recommendationStore.ts
import { get, writable } from 'svelte/store';
import type { Movie } from '../types/movie';
import { movies } from './movieStore';
import { fetchMovieDetails } from './api/imdb';

const LOCAL_URL = import.meta.env.VITE_LOCAL_URL;

interface JobStatus {
  id: string;
  status: string;
  results?: Movie[];
  error?: string;
}

const DEFAULT_PARAMS: AlgorithmParams = {
  knn_item: {
    k: 5,
    minCommonItems: 3
  },
  knn_user: {
    k: 10,
    moviesToConsider: 50,
    minCommonUsers: 5
  },
  content_based: {
    minSimilarity: 0.5
  },
  svd: {
    // Empty object as per interface
  },
  fixedReturns: 10
};

export interface AlgorithmParams {
  knn_item: {
      k: number;
      minCommonItems: number;
      
  };
  knn_user: {
      k: number;
      
      moviesToConsider: number;
      minCommonUsers: number;
  };
  content_based: {
    minSimilarity: number;
  };
  svd: {
      
  };
  fixedReturns: number;
};

export let selectedAlgorithm = writable<string>("content_based");
export let isLoading = writable<boolean>(false);
export let algorithmParams = writable<AlgorithmParams>(DEFAULT_PARAMS);
export let jobStatus = writable<string>("");

async function startRecommendationJob(ratings: Array<{imdb_id: string, rating: number}>, algorithm: string, params: AlgorithmParams) {
  const response = await fetch(`${LOCAL_URL}/api/recommendations/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ratings, algorithm, params })
  });
  
  if (!response.ok) throw new Error('Failed to start recommendation job');
  return response.json();
}

export async function checkIfMovieInDB(movies: string[]) {
  const response = await fetch(`${LOCAL_URL}/api/movies/check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ movies })
  });

  if (!response.ok) throw new Error('Failed to check if movies were in the db');
  return response.json();

}

export async function fuzzyFindMoviesFromDB(title: string) {
  const response = await fetch(`${LOCAL_URL}/api/movies/find/${title}`);

  if (!response.ok) throw new Error('Failed to check if movies were in the db');
  return response.json();

}

async function checkJobStatus(jobId: string) {
  const response = await fetch(`${LOCAL_URL}/api/recommendations/status/${jobId}`);
  if (!response.ok) throw new Error('Failed to check job status');
  return response.json();
}

export async function enrichRecommendationStore(movieIds: string[]): Promise<Movie[]> {
  const movieInfos = await Promise.all(
    movieIds.map(id => fetchMovieDetails(id))
  );
  return movieInfos.filter((movie): movie is Movie => movie !== null)
}

function createRecommendationStore() {
  const { subscribe, set } = writable<Movie[]>([]);
  let pollInterval: number | null = null;

  return {
    subscribe,
    set,
    generateRecommendations: async (algorithm: string, params: AlgorithmParams) => {
      try {
        // Get rated movies
        const ratedMovies = get(movies).filter(m => m.rating > 0);
        const ratings = ratedMovies.map(movie => ({
          imdb_id: movie.id,
          rating: movie.rating
        }));

        // Start the job
        const { jobId } = await startRecommendationJob(ratings, algorithm, params);
        
        // Poll for results
        return new Promise((resolve, reject) => {
          pollInterval = window.setInterval(async () => {
            try {
              const status = await checkJobStatus(jobId);
              console.log(status.status)
              jobStatus.set(status.status);
              if (status.status === 'completed') {
                clearInterval(pollInterval!);
                // Create an array to store all movies
                const recommendedMovies: Movie[] = status.results.map(res => ({
                    id: res.id,
                    title: res.title,
                    rating: 0,
                    genre: '',
                    year: res.year,
                    poster: null,
                    plot: '',
                    imdbRating: 0,
                    tmdbId: 0
                }));

                // Set all movies at once
                set(recommendedMovies);
                resolve(recommendedMovies);
              } else if (status.status === 'failed') {
                clearInterval(pollInterval!);
                reject(new Error(status.error || 'Job failed'));
              }
              // Continue polling if status is 'pending'
            } catch (error) {
              clearInterval(pollInterval!);
              reject(error);
            }
          }, 1000); // Poll every second
          
          // Stop polling after 30 seconds
          setTimeout(() => {
            if (pollInterval) {
              clearInterval(pollInterval);
              reject(new Error('Recommendation timeout'));
            }
          }, 120000);
        });
      } catch (error) {
        console.error('Failed to generate recommendations:', error);
        throw error;
      }
    },
    cleanup: () => {
      if (pollInterval) clearInterval(pollInterval);
    }
  };
}

export const recommendations = createRecommendationStore();