export interface StockData {
  ticker: string
  price: number
  price_change_1d: number
  price_change_5d: number
  rsi: number
  rsi_status: string
  macd: number
  macd_signal: number
  ema20: number
  bollinger_high: number
  bollinger_low: number
  atr: number
  trend: string
  volume: number
  last_updated: string
}

export interface NewsItem {
  title: string
  url: string
  source: string
  published_at: string
  content: string
  sentiment: string
  confidence: number
}

export interface Signal {
  ticker: string
  signal: string
  signals: string[]
  reasoning: string[]
  generated_at: string
}

export interface DashboardData {
  stocks: StockData[]
  news: NewsItem[]
  signals: Signal[]
  timestamp: string
}