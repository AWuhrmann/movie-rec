// movieStore.ts
import { writable } from 'svelte/store';
import type { Movie } from '../types/movie';

// Interface for storing ratings and movie data
interface StoredMovie {
  movieData: Movie;
  rating: number;
}

// Function to safely access localStorage
function getLocalStorage() {
  if (typeof window !== 'undefined') {
    return window.localStorage;
  }
  return null;
}

// Function to load rated movies from localStorage
function loadRatedMovies(): StoredMovie[] {
  const storage = getLocalStorage();
  if (!storage) return [];
  
  const stored = storage.getItem('ratedMovies');
  return stored ? JSON.parse(stored) : [];
}

// Function to save rated movies to localStorage
function saveRatedMovies(movies: Movie[]): void {
  const storage = getLocalStorage();
  if (!storage) return;
  
  const ratedMovies = movies
    .filter(movie => movie.rating > 0)
    .map(movie => ({
      movieData: movie,
      rating: movie.rating
    }));
  
  storage.setItem('ratedMovies', JSON.stringify(ratedMovies));
}

function createMovieStore() {
  // Load rated movies from localStorage
  const storedMovies = loadRatedMovies();
  const { subscribe, set, update } = writable<Movie[]>([]);

  return {
    subscribe,
    set: (movies: Movie[]) => {
      // When setting new movies, merge with stored rated movies
      const ratedMoviesMap = new Map(
        storedMovies.map(stored => [stored.movieData.id, stored])
      );
      
      const mergedMovies = movies.map(movie => {
        const stored = ratedMoviesMap.get(movie.id);
        if (stored) {
          return { ...movie, rating: stored.rating };
        }
        return movie;
      });

      // Add any stored rated movies that aren't in the current set
      storedMovies.forEach(stored => {
        if (!mergedMovies.some(m => m.id === stored.movieData.id)) {
          mergedMovies.push({ ...stored.movieData, rating: stored.rating });
        }
      });

      set(mergedMovies);
    },
    updateRating: (movieId: string, rating: number) => {
      update(movies => {
        const updatedMovies = movies.map(movie =>
          movie.id === movieId 
            ? { ...movie, rating }
            : movie
        );
        saveRatedMovies(updatedMovies);
        return updatedMovies;
      });
    },
    removeRating: (movieId: string) => {
      update(movies => {
        const updatedMovies = movies.map(movie =>
          movie.id === movieId 
            ? { ...movie, rating: 0 }
            : movie
        );
        saveRatedMovies(updatedMovies);
        return updatedMovies;
      });
    },
    resetAllRatings: () => {
      const storage = getLocalStorage();
      if (storage) {
        storage.removeItem('ratedMovies');
      }
      update(movies => {
        const resetMovies = movies.map(movie => ({ ...movie, rating: 0 }));
        return resetMovies;
      });
    }
  };
}

export const movies = createMovieStore();