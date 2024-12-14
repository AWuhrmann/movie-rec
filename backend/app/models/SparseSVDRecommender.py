import numpy as np
import joblib
import os
import time
from scipy.sparse import csr_matrix
from sklearn.metrics import mean_squared_error, mean_absolute_error

class SparseSVDRecommender:
    def __init__(self, n_factors: int = 100, learning_rate: float = 0.005,
                 regularization: float = 0.02, n_epochs: int = 20):
        """
        Initialize the SVD recommender system with verbose logging and serialization.
        """
        self.n_factors = n_factors
        self.learning_rate = learning_rate
        self.regularization = regularization
        self.n_epochs = n_epochs

        # Model parameters
        self.user_factors = None
        self.item_factors = None
        self.user_biases = None
        self.item_biases = None
        self.global_mean = None

        # Mapping dictionaries
        self.user_id_map = {}
        self.movie_id_map = {}
        self.reverse_user_id_map = {}
        self.reverse_movie_id_map = {}


    def fit(self, ratings_matrix_train: csr_matrix, 
            user_id_map: dict = None, 
            movie_id_map: dict = None) -> 'SparseSVDRecommender3':
        """
        Train the model using a pre-computed sparse ratings matrix.
        
        Args:
            ratings_matrix_train (csr_matrix): Sparse training ratings matrix
            user_id_map (dict, optional): Mapping of original user IDs to matrix indices
            movie_id_map (dict, optional): Mapping of original movie IDs to matrix indices
        """
        print("\n--- Starting SVD Training ---")
        start_total_time = time.time()

        # If maps are not provided, create default mappings
        if user_id_map is None:
            self.user_id_map = {i: i for i in range(ratings_matrix_train.shape[0])}
            self.reverse_user_id_map = self.user_id_map
        else:
            self.user_id_map = user_id_map
            self.reverse_user_id_map = {idx: user for user, idx in user_id_map.items()}

        if movie_id_map is None:
            self.movie_id_map = {i: i for i in range(ratings_matrix_train.shape[1])}
            self.reverse_movie_id_map = self.movie_id_map
        else:
            self.movie_id_map = movie_id_map
            self.reverse_movie_id_map = {idx: movie for movie, idx in movie_id_map.items()}

            # Compute global mean
        self.global_mean = ratings_matrix_train.data.mean()
        print(f"Global mean rating: {self.global_mean:.2f}")

        # Get matrix dimensions
        n_users, n_items = ratings_matrix_train.shape
        print(f"Matrix dimensions: {n_users} users x {n_items} movies")

        # Initialize matrices
        self._init_matrices(n_users, n_items)

        # Get indices of non-zero elements
        users, items = ratings_matrix_train.nonzero()
        total_ratings = len(users)
        print(f"Total ratings to train on: {total_ratings}")

            # Training loop
        for epoch in range(self.n_epochs):
            epoch_start_time = time.time()

            # Shuffle the order of training examples
            shuffle_indices = np.random.permutation(len(users))

            # Track total error for the epoch
            total_error = 0

            for idx in shuffle_indices:
                u, i = users[idx], items[idx]
                r = ratings_matrix_train[u, i]

                # Compute current prediction
                pred = (self.global_mean +
                        self.user_biases[u] +
                        self.item_biases[i] +
                        self.user_factors[u] @ self.item_factors[i])

                # Compute error
                error = r - pred
                total_error += error ** 2

                # Update biases and factors
                self.user_biases[u] += self.learning_rate * (error - self.regularization * self.user_biases[u])
                self.item_biases[i] += self.learning_rate * (error - self.regularization * self.item_biases[i])

                user_factors_update = (error * self.item_factors[i] -
                                       self.regularization * self.user_factors[u])
                item_factors_update = (error * self.user_factors[u] -
                                       self.regularization * self.item_factors[i])

                self.user_factors[u] += self.learning_rate * user_factors_update
                self.item_factors[i] += self.learning_rate * item_factors_update

            # Print epoch summary
            rmse = np.sqrt(total_error / total_ratings)
            epoch_time = time.time() - epoch_start_time
            print(f"Epoch {epoch + 1}/{self.n_epochs}: RMSE = {rmse:.4f}, Time = {epoch_time:.2f}s")

        # Final training summary
        total_training_time = time.time() - start_total_time
        print(f"\n--- Training Complete ---")
        print(f"Total training time: {total_training_time:.2f} seconds")

        return self

    def evaluate(self, ratings_matrix_test: csr_matrix, 
         include_unrated: bool = False):
        """
        Evaluate model performance on test sparse matrix.
        
        Args:
            ratings_matrix_test (csr_matrix): Sparse test ratings matrix
            include_unrated (bool): Whether to include predictions for unrated items

        Returns:
            Dict with performance metrics, actual ratings, and predictions
        """
        print("\n--- Model Evaluation ---")
        
        # Compute predictions for test set
        predictions = []
        actual_ratings = []
        
        # Get test set non-zero indices
        test_users, test_items = ratings_matrix_test.nonzero()
        
        for idx in range(len(test_users)):
            u, i = test_users[idx], test_items[idx]
            actual_rating = ratings_matrix_test[u, i]
            
            # Translate back to original IDs if needed
            orig_user_id = self.reverse_user_id_map.get(u, u)
            orig_movie_id = self.reverse_movie_id_map.get(i, i)
            
            try:
                pred = self.predict(orig_user_id, orig_movie_id)
                predictions.append(pred)
                actual_ratings.append(actual_rating)
            except Exception as e:
                print(f"Prediction error for user {u}, movie {i}: {e}")
                continue
        
        # Compute metrics
        rmse = np.sqrt(mean_squared_error(actual_ratings, predictions))
        mae = mean_absolute_error(actual_ratings, predictions)
        
        print("Performance Metrics:")
        print(f"RMSE: {rmse:.4f}")
        print(f"MAE: {mae:.4f}")
        print(f"Total Test Ratings: {len(actual_ratings)}")
        
        return {
            'RMSE': rmse,
            'MAE': mae,
            'Total Test Ratings': len(actual_ratings)
        }, actual_ratings, predictions

    def save_model(self, filepath: str = 'svd_recommender_model.joblib'):
        """Save the entire model state to a file."""
        try:
            if self.user_factors is None:
                raise ValueError("Model must be trained before saving")

            model_state = {
                'user_factors': self.user_factors,
                'item_factors': self.item_factors,
                'user_biases': self.user_biases,
                'item_biases': self.item_biases,
                'global_mean': self.global_mean,
                'user_id_map': self.user_id_map,
                'movie_id_map': self.movie_id_map,
                'n_factors': self.n_factors,
                'learning_rate': self.learning_rate,
                'regularization': self.regularization,
                'n_epochs': self.n_epochs
            }

            joblib.dump(model_state, filepath)
            print(f"Model successfully saved to {filepath}")

        except Exception as e:
            print(f"Error saving model: {e}")

    def load_model(self, filepath: str = 'svd_recommender_model.joblib'):
        """Load a previously saved model state."""
        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"No model file found at {filepath}")

            model_state = joblib.load(filepath)

            # Restore model parameters
            self.user_factors = model_state['user_factors']
            self.item_factors = model_state['item_factors']
            self.user_biases = model_state['user_biases']
            self.item_biases = model_state['item_biases']
            self.global_mean = model_state['global_mean']

            # Restore mapping dictionaries
            self.user_id_map = model_state['user_id_map']
            self.movie_id_map = model_state['movie_id_map']

            # Recreate reverse mapping dictionaries
            self.reverse_user_id_map = {idx: user for user, idx in self.user_id_map.items()}
            self.reverse_movie_id_map = {idx: movie for movie, idx in self.movie_id_map.items()}

            print(f"Model successfully loaded from {filepath}")
            print(f"Loaded model details:")
            print(f"  - Latent Factors: {model_state['n_factors']}")
            print(f"  - Unique Users: {len(self.user_id_map)}")
            print(f"  - Unique Movies: {len(self.movie_id_map)}")

            return self

        except Exception as e:
            print(f"Error loading model: {e}")
            return None

    def _init_matrices(self, n_users: int, n_items: int):
        """Initialize model parameters with logging."""
        print(f"\nInitializing matrices with {self.n_factors} latent factors")
        self.user_factors = np.random.normal(0, 0.1, (n_users, self.n_factors))
        self.item_factors = np.random.normal(0, 0.1, (n_items, self.n_factors))
        self.user_biases = np.zeros(n_users)
        self.item_biases = np.zeros(n_items)

    def predict(self, user_id: int, movie_id: int) -> float:
        """Predict rating with error handling and logging."""
        if self.user_factors is None:
            print("Error: Model must be trained before making predictions")
            return None

        try:
            u_idx = self.user_id_map[user_id]
            m_idx = self.movie_id_map[movie_id]
        except KeyError:
            return self.global_mean

        prediction = (self.global_mean +
                      self.user_biases[u_idx] +
                      self.item_biases[m_idx] +
                      self.user_factors[u_idx] @ self.item_factors[m_idx])

        return prediction

    def recommend_items(self, user_id: int, n_items: int = 10,
                        exclude_rated: bool = True):
        """Recommend items with detailed logging."""
        if self.user_factors is None:
            print("Error: Model must be trained before making recommendations")
            return []

        try:
            u_idx = self.user_id_map[user_id]
        except KeyError:
            print(f"Warning: User {user_id} not found in training data")
            return []

        # Calculate predictions for all items
        user_vector = (self.global_mean +
                       self.user_biases[u_idx] +
                       self.user_factors[u_idx] @ self.item_factors.T)

        # Create array of (movie_id, prediction) tuples
        predictions = []
        for m_idx, pred in enumerate(user_vector):
            movie_id = self.reverse_movie_id_map[m_idx]
            predictions.append((movie_id, pred))

        # Sort by predicted rating
        predictions.sort(key=lambda x: x[1], reverse=True)

        # Optional: exclude already rated movies
        if exclude_rated:
            rated_movies = set(df_filtered[df_filtered['sparse_user_id'] == user_id]['sparse_movie_id'])
            predictions = [rec for rec in predictions if rec[0] not in rated_movies]

        return predictions

    def handle_new_user(self, user_ratings, n_items=10):
        """
        Incorporate new user ratings into recommendations without full retraining

        Args:
            user_ratings (pd.DataFrame): DataFrame with columns 'movieId' and 'rating'
            n_items (int): Number of recommendations to return

        Returns:
            List of recommended movie IDs
        """
        # Check if model is trained
        if self.user_factors is None:
            raise ValueError("Model must be trained first")

        # Validate movie IDs exist in original training data
        valid_movies = [mid for mid in user_ratings['sparse_movie_id'] if mid in self.movie_id_map]
        valid_ratings = user_ratings[user_ratings['sparse_movie_id'].isin(valid_movies)]

        if len(valid_movies) == 0:
            print("No valid movie ratings found")
            return []

        # Ensure consistent dimensionality
        new_user_factors = np.zeros(self.item_factors.shape[1])
        new_user_bias = 0

        for _, row in valid_ratings.iterrows():
            movie_idx = self.movie_id_map[row['sparse_movie_id']]

            # Safely handle potential shape mismatches
            movie_factors = self.item_factors[movie_idx]

            # Ensure correct dimensionality
            if len(movie_factors) != len(new_user_factors):
                # Truncate or pad the movie factors to match new_user_factors
                if len(movie_factors) > len(new_user_factors):
                    movie_factors = movie_factors[:len(new_user_factors)]
                else:
                    padded_factors = np.zeros(len(new_user_factors))
                    padded_factors[:len(movie_factors)] = movie_factors
                    movie_factors = padded_factors

            # Update user vector with weighted item factors
            new_user_factors += row['rating'] * movie_factors
            new_user_bias += row['rating'] - self.global_mean

        # Normalize by number of ratings
        new_user_factors /= len(valid_ratings)
        new_user_bias /= len(valid_ratings)

        # Compute predictions for all items
        predictions = (self.global_mean +
                       new_user_bias +
                       new_user_factors @ self.item_factors.T)

        predictions = np.clip(predictions, None, 5)

        def normalize_rating(predicted_rating, min_pred, max_pred, min_rating, max_rating):
            return min_rating + (predicted_rating - min_pred) * (max_rating - min_rating) / (max_pred - min_pred)

        def transform_rating(predicted_rating, min_rating, max_rating):
            range_width = max_rating - min_rating
            return min_rating + range_width / (1 + np.exp(-predicted_rating))

        #print("normalizing")
        predictions = transform_rating(predictions, 0.5, 5)  
        #predictions = normalize_rating(predictions, np.min(predictions), np.max(predictions), 0.5, 5)

        # Create and sort recommendations
        recommendations = [
            (self.reverse_movie_id_map[idx], pred)
            for idx, pred in enumerate(predictions)
        ]
        recommendations.sort(key=lambda x: x[1], reverse=True)

        # Exclude movies already rated
        rated_movies = set(valid_ratings['sparse_movie_id'])
        recommendations = [rec for rec in recommendations if rec[0] not in rated_movies]

        return recommendations