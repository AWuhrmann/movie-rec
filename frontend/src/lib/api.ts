import { API_BASE_URL } from './config';

export async function startRecommendations(ratings: Array<{imdb_id: string, rating: number}>) {
  const response = await fetch(`${API_BASE_URL}/recommendations/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ratings })
  });
  
  if (!response.ok) throw new Error('Failed to start recommendation job');
  return response.json();
}

export async function checkRecommendationStatus(jobId: string) {
  const response = await fetch(`${API_BASE_URL}/recommendations/status/${jobId}`);
  if (!response.ok) throw new Error('Failed to check job status');
  return response.json();
}