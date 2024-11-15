import { describe, it, expect } from 'vitest';
import { get } from 'svelte/store';
import { movies } from './movieStore';
import type { Movie } from '../types/movie';

describe('Movie Store', () => {
  it('should initialize with movies', () => {
    const movieList = get(movies);
    expect(movieList.length).toBe(3);
    expect(movieList[0].title).toBe('The Matrix');
  });

  it('should update movie rating', () => {
    movies.update(items =>
      items.map(movie =>
        movie.id === 1 ? { ...movie, rating: 5 } : movie
      )
    );

    const updatedMovies = get(movies);
    expect(updatedMovies.find(m => m.id === 1)?.rating).toBe(5);
  });
});