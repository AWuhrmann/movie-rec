// recommendationStore.ts
import { get, writable } from 'svelte/store';
import type { Movie } from '../types/movie';
import { movies } from './movieStore';
import { fetchMovieDetails } from './api/imdb';

interface JobStatus {
  id: string;
  status: 'pending' | 'completed' | 'failed';
  results?: Movie[];
  error?: string;
}


async function startRecommendationJob(ratings: Array<{imdb_id: string, rating: number}>, algorithm: string) {
  const response = await fetch('/api/recommendations/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ratings, algorithm })
  });
  
  if (!response.ok) throw new Error('Failed to start recommendation job');
  return response.json();
}

async function checkJobStatus(jobId: string) {
  const response = await fetch(`/api/recommendations/status/${jobId}`);
  if (!response.ok) throw new Error('Failed to check job status');
  return response.json();
}

async function enrichRecommendationStore(movieIds: string[]): Promise<Movie[]> {
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
    generateRecommendations: async (algorithm: string) => {
      try {
        // Get rated movies
        const ratedMovies = get(movies).filter(m => m.rating > 0);
        const ratings = ratedMovies.map(movie => ({
          imdb_id: movie.id,
          rating: movie.rating
        }));

        // Start the job
        const { jobId } = await startRecommendationJob(ratings, algorithm);
        
        // Poll for results
        return new Promise((resolve, reject) => {
          pollInterval = window.setInterval(async () => {
            try {
              const status = await checkJobStatus(jobId);
              console.log(status.status)
              if (status.status === 'completed') {
                clearInterval(pollInterval!);
                console.log(status.results);
                const movieNames = await enrichRecommendationStore(status.results)

                set(movieNames);
                resolve(status.results);
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
          }, 30000);
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