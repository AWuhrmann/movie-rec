import { writable } from 'svelte/store';
import type { Movie } from '../types/movie';

function createRecommendationStore() {
  const { subscribe, set } = writable<Movie[]>([]);

  return {
    subscribe,
    set,
    generateRecommendations: () => {
      // For now, just generate random recommendations
      // This would be replaced with actual recommendation logic
      const dummyRecommendations: Movie[] = [
        {
          id: 'rec1',
          title: 'Recommended Movie 1',
          year: '2024',
          genre: 'Action',
          rating: 0,
          posterPath: null,
          poster: null,
          tmdbId: -1,
          plot: 'A recommended movie plot',
          imdbRating: '8.5'
        },
        // Add more dummy recommendations as needed
      ];
      set(dummyRecommendations);
    }
  };
}

export const recommendations = createRecommendationStore();