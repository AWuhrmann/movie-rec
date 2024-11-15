export interface Movie {
    id: string;
    title: string;
    rating: number;
    genre: string;
    year: string;
    posterPath: string | null;
    tmdbId: number;
    poster: string | null;
    plot: string;
    imdbRating: string;
}