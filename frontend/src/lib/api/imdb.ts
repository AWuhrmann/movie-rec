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
    const searchUrl = `${BASE_URL}?apikey=${OMDB_API_KEY}&s=${encodeURIComponent(query)}`;
    console.log('Search URL:', searchUrl); // For debugging
    
    const searchResponse = await fetch(searchUrl);
    const searchData: OMDBSearchResponse = await searchResponse.json();
    
    if (searchData.Response === "False" || !searchData.Search) {
      console.log("No results found");
      return [];
    }

    // Get detailed info for each movie
    const movies = await Promise.all(
      searchData.Search.slice(0, 5).map(async (item) => {
        try {
          const detailUrl = `${BASE_URL}?apikey=${OMDB_API_KEY}&i=${item.imdbID}`;
          console.log('Detail URL:', detailUrl); // For debugging
          
          const detailResponse = await fetch(detailUrl);
          const movieData: OMDBDetailResponse = await detailResponse.json();
          
          if (movieData.Response === "True") {
            return {
              id: movieData.imdbID,
              title: movieData.Title,
              rating: 0,
              genre: movieData.Genre,
              year: movieData.Year,
              poster: movieData.Poster !== "N/A" ? movieData.Poster : null,
              plot: movieData.Plot,
              imdbRating: movieData.imdbRating
            };
          }
          return null;
        } catch (error) {
          console.error('Error fetching movie details:', error);
          return null;
        }
      })
    );

    // Filter out any null values from failed requests
    return movies.filter((movie): movie is Movie => movie !== null);
  } catch (error) {
    console.error('Error in searchMovies:', error);
    return [];
  }
}