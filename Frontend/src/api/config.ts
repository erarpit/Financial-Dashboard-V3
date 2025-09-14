// API Configuration
export const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // Dashboard endpoints
  DASHBOARD: '/dashboard',
  STOCK_DATA: '/stock-data',
  HISTORICAL_DATA: '/historical-data',
  
  // News endpoints
  NEWS: '/news',
  NEWS_ANALYSIS: '/news-analysis',
  
  // Signals endpoints
  SIGNALS: '/signals',
  AI_SIGNALS: '/ai-signals',
  
  // Domain endpoints
  SECTORS: '/sectors',
  INDUSTRIES: '/industries',
  DOMAIN_OVERVIEW: '/domain-overview',
  
  // Market endpoints
  MARKET_STATUS: '/market-status',
  MARKET_SUMMARY: '/market-summary',
  
  // Ownership endpoints
  OWNERSHIP: '/ownership',
  INSIDER_TRADING: '/insider-trading',
  
  // FastInfo endpoints
  FAST_INFO: '/fast-info',
  
  // Quote endpoints
  QUOTE: '/quote',
  QUOTE_INFO: '/quote-info',
  
  // Query Builder endpoints
  QUERY_FIELDS: '/query-builder/fields',
  QUERY_VALUES: '/query-builder/values',
  QUERY_VALIDATE: '/query-builder/validate',
  QUERY_EXECUTE_EQUITY: '/query-builder/execute/equity',
  QUERY_EXECUTE_FUND: '/query-builder/execute/fund',
  QUERY_PREDEFINED: '/query-builder/predefined',
  
  // Enhanced YFinance endpoints
  ENHANCED_DOWNLOAD: '/enhanced-download',
  BULK_DOWNLOAD: '/bulk-download',
  TECHNICAL_INDICATORS: '/enhanced-download/indicators',
  
  // Health check
  HEALTH: '/health'
} as const;

export const API_TIMEOUT = 30000; // 30 seconds
export const MAX_RETRIES = 3;
