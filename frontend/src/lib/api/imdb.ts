import { checkIfMovieInDB, fuzzyFindMoviesFromDB } from "$lib/recommendationStore";
import type { Movie } from "../../types/movie";

const OMDB_API_KEY = import.meta.env.VITE_IMDB_API_KEY;
const IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500';

const BASE_URL = 'https://www.omdbapi.com'; // Changed from img.omdbapi.com

interface OMDBSearchResponse {
  Search?: Array<{
    Title: string;
    Year: string;
    imdbID: string;
    Type: string;
    Poster: string;
  }>;
  Response: string;
  Error?: string;
}

interface OMDBDetailResponse {
  Title: string;
  Year: string;
  Genre: string;
  Plot: string;
  Poster: string;
  imdbRating: string;
  imdbID: string;
  Response: string;
}

export async function searchMovies(query: string): Promise<Movie[]> {
  try {
    // Get matching movies from your database
    const dbMovies: DBMovie[] = await fuzzyFindMoviesFromDB(query);
    
    if (!dbMovies.length) {
      console.log('No movies found in database for query:', query);
      return [];
    }

    console.log(dbMovies);

    // Fetch detailed information for each movie
    const movieDetailsPromises = dbMovies.map(async (dbMovie) => {
      try {
        const movieDetails = await fetchMovieDetails(dbMovie.imdb_id);
        if (movieDetails) {
          return movieDetails;
        } else {
          // Fallback to basic info from database if API fetch fails
          return {
            id: dbMovie.imdb_id,
            title: dbMovie.title,
            rating: 0,
            genre: '',
            year: '',
            poster: null,
            plot: '',
            imdbRating: 0,
            tmdbId: 0
          };
        }
      } catch (error) {
        // If there's any error, return basic info from database
        console.error(`Error fetching details for ${dbMovie.title}:`, error);
        return {
          id: dbMovie.imdb_id,
          title: dbMovie.title,
          rating: 0,
          genre: '',
          year: '',
          poster: null,
          plot: '',
          imdbRating: 0,
          tmdbId: 0
        };
      }
    });

    // Wait for all movie details to be fetched
    const movies = await Promise.all(movieDetailsPromises);
    
    console.log(`Found ${movies.length} movies for query: ${query}`);
    return movies;

  } catch (error) {
    console.error('Error in searchMovies:', error);
    return [];
  }
}

export async function fetchMovieDetails(imdbId: string): Promise<Movie | null> {
  try {
    // Create URL for direct ID lookup
    const detailUrl = `${BASE_URL}?apikey=${OMDB_API_KEY}&i=${encodeURIComponent(imdbId)}`;
    console.log('Fetching details for:', imdbId);

    const response = await fetch(detailUrl);
    const movieData: OMDBDetailResponse = await response.json();

    // Check if we got a valid response
    if (movieData.Response === "True") {
      return {
        id: movieData.imdbID,
        title: movieData.Title,
        rating: 0,
        genre: movieData.Genre,
        year: movieData.Year,
        poster: movieData.Poster !== "N/A" ? movieData.Poster : null,
        plot: movieData.Plot,
        imdbRating: movieData.imdbRating,
        // Add any other required fields from your Movie type
        tmdbId: 0 // If you need this, you'll need to get it from another source
      };
    }

    console.log('No valid movie data found for:', imdbId);
    return null;

  } catch (error) {
    console.error('Error fetching movie details for', imdbId, ':', error);
    return null;
  }
}