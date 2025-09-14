import axios from 'axios';
// Type declarations moved to vite-env.d.ts

/**
 * The base URL for API requests.
 *
 * This constant retrieves the API base URL from the environment variable `VITE_API_BASE`.
 * If the environment variable is not set, it defaults to `'http://localhost:8000'`.
 *
 * @remarks
 * This allows the frontend to dynamically target different backend endpoints
 * depending on the deployment environment (development, staging, production, etc.).
 */
const API_BASE =
  typeof import.meta !== 'undefined' &&
  typeof (import.meta as any).env !== 'undefined' &&
  (import.meta as any).env.VITE_API_BASE
    ? (import.meta as any).env.VITE_API_BASE
    : 'http://localhost:8000';

/**
 * Sanitizes ticker strings by removing extra quotes and whitespace,
 * and converts to uppercase.
 *
 * @param ticker - The ticker string to sanitize.
 * @returns The cleaned ticker string.
 */
export const cleanTicker = (ticker: string): string =>
  ticker.replace(/^['"]+|['"]+$/g, '').toUpperCase();

/**
 * Fetches dashboard data for the specified stock tickers.
 *
 * Sends a GET request to the `/dashboard` endpoint with the provided tickers as a comma-separated list.
 *
 * @param tickers - An array of stock ticker symbols to retrieve dashboard data for.
 * @returns A promise that resolves to the dashboard data returned by the API.
 */
export const getDashboardData = async (tickers: string[]) => {
  console.log('API_BASE:', API_BASE);
  console.log('Requesting tickers:', tickers.join(','));
  const response = await axios.get(`${API_BASE}/dashboard`, {
    params: { tickers: tickers.join(',') }
  });
  console.log('API Response:', response.data);
  return response.data;
};

/**
 * Fetches individual stock data for a given ticker.
 *
 * @param ticker - The stock ticker symbol.
 * @returns A promise that resolves to the stock data returned by the API.
 */
export const getStockData = async (ticker: string) => {
  const cleanSymbol = cleanTicker(ticker);
  const response = await axios.get(`${API_BASE}/stocks/${cleanSymbol}`);
  return response.data;
};

/**
 * Fetches news items with an optional limit.
 *
 * @param limit - Number of news items to fetch (default is 10).
 * @returns A promise that resolves to the news data returned by the API.
 */
export const getNews = async (limit: number = 10) => {
  const response = await axios.get(`${API_BASE}/news`, {
    params: { limit }
  });
  return response.data;
};

/**
 * Fetches trading signals for a given ticker.
 *
 * @param ticker - The stock ticker symbol.
 * @returns A promise that resolves to the signals data returned by the API.
 */
export const getSignals = async (ticker: string) => {
  const cleanSymbol = cleanTicker(ticker);
  const response = await axios.get(`${API_BASE}/signals/${cleanSymbol}`);
  return response.data;
};

/**
 * Performs a health check on the backend API.
 *
 * @returns A promise that resolves to the health check data.
 */
export const healthCheck = async () => {
  const response = await axios.get(`${API_BASE}/health`);
  return response.data;
};
