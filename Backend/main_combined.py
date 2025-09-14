# Combined FastAPI Application - Financial Dashboard with AI Assistant
# Merges main.py and enhanced-main.py for complete functionality
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

# Import services
from services.market_data import get_stock_data, get_historical_data
from services.news_scraper import get_financial_news, NewsItem
from services.sentiment_analysis import analyze_sentiment
from services.signals import generate_signals
from services.domain_service import domain_service
from services.market_service import market_service
from services.holders_service import holders_service
from services.fastinfo_service import fastinfo_service
from services.quote_service import quote_service
from services.query_builder_service import query_builder_service
from services.enhanced_yfinance import enhanced_downloader

# Import new pipelines
try:
    from pipelines.assistant import ask_ai_assistant, QueryTemplates
    from pipelines.volume_analysis import analyze_volume, compute_volume_signal
    from pipelines.live_data import get_live_quote, get_popular_stocks_data
    from pipelines.news import get_recent_news
    from pipelines.enhanced_analysis import get_enhanced_analysis, get_analyst_summary, get_earnings_estimates
except ImportError as e:
    print(f"Some pipeline imports failed: {e}")
    # Create fallback functions if needed

# Import models and schemas
from models.database import init_db, get_cached_data, cache_data
from models.schemas import (
    StockData, Signal, DashboardResponse, SectorData, IndustryData, MarketStatus, MarketSummary, 
    OwnershipData, FastInfoData, QuoteData, SustainabilityData, RecommendationData, CalendarData,
    TechnicalIndicators, VolumeAnalysis, PriceMomentum, AISignal, EnhancedStockData, MarketSentiment,
    NewsAnalysis, PatternAnalysis, AIDashboardResponse, QueryBuilderResult, EnhancedDownloadResult,
    BulkAnalysisResult, ErrorResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    logger.info("🚀 Starting Financial Dashboard API with AI Assistant")
    init_db()
    yield
    # Shutdown
    logger.info("⏹️ Shutting down Financial Dashboard API")

# Initialize FastAPI app
app = FastAPI(
    title="Financial Dashboard with AI Assistant",
    description="Intelligent stock market analysis dashboard with AI-powered insights, caching, and comprehensive analysis",
    version="2.0.0",
    lifespan=lifespan
)

# Add router registration (moved after app initialization)
try:
    from routers.patterns import router as patterns_router
    app.include_router(patterns_router)
except ImportError:
    logger.warning("Patterns router not available - skipping pattern endpoints")

# Middleware
app.add_middleware(GZipMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],  # Frontend URLs + wildcard for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= BASIC ENDPOINTS =============

@app.get("/")
async def root():
    return {"message": "Financial Dashboard API with AI Assistant", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "features": ["AI Assistant", "Volume Analysis", "Live Data", "Sentiment Analysis", "Caching", "Patterns", "Enhanced Analysis", "Analyst Data", "Earnings Estimates", "Domain Analysis", "Sector Data", "Industry Data", "Market Status", "Ownership Data", "Insider Trading", "FastInfo", "Quote Data", "Sustainability", "Recommendations", "Query Builder", "Stock Screening", "Enhanced YFinance", "Bulk Download", "Technical Indicators"]
    }

# ============= STOCK DATA ENDPOINTS =============

@app.get("/stocks/{ticker}")
async def get_stock(
    ticker: str, 
    period: str = "6mo", 
    interval: str = "1d"
) -> StockData:
    """Get stock data for a specific ticker with caching."""
    try:
        # Check cache first
        cache_key = f"stock_{ticker}_{period}_{interval}"
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        # Fetch fresh data
        data = await get_stock_data(ticker, period, interval)
        cache_data(cache_key, data, expiry_minutes=5)
        return data
    except Exception as e:
        logger.error(f"Error fetching stock data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/live")
async def get_live_data(ticker: str = Query(..., description="Stock ticker symbol")):
    """Get real-time/delayed market data for a ticker."""
    try:
        live_data = get_live_quote(ticker)
        return live_data
        
    except Exception as e:
        logger.error(f"Live data error for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch live data: {str(e)}")

@app.get("/popular-stocks")
async def get_popular_stocks():
    """Get data for popular Indian stocks."""
    try:
        popular_data = get_popular_stocks_data()
        return popular_data
        
    except Exception as e:
        logger.error(f"Popular stocks error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch popular stocks: {str(e)}")

# ============= NEWS ENDPOINTS =============

@app.get("/news")
async def get_news(limit: int = Query(10, description="Number of news items to return")) -> List[NewsItem]:
    """Get financial news with caching and sentiment analysis."""
    try:
        cache_key = f"news_{limit}"
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        # Try enhanced news first, fallback to original
        try:
            news_items = get_recent_news(limit=limit)
            
            # Add sentiment analysis to each news item
            for item in news_items:
                if isinstance(item, dict) and 'content' in item:
                    sentiment = analyze_sentiment(item.get('content', '') + ' ' + item.get('title', ''))
                    item['sentiment_analysis'] = sentiment
            
            cache_data(cache_key, news_items, expiry_minutes=15)
            return news_items
            
        except Exception as e:
            logger.warning(f"Enhanced news failed, using fallback: {str(e)}")
            news = await get_financial_news(limit)
            cache_data(cache_key, news, expiry_minutes=15)
            return news
            
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= SIGNALS ENDPOINTS =============

@app.get("/signals/{ticker}")
async def get_signal(ticker: str) -> Signal:
    """Get trading signals for a ticker with caching."""
    try:
        cache_key = f"signal_{ticker}"
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        # Get stock data and news for analysis
        stock_data = await get_stock_data(ticker)
        news = await get_financial_news(5)
        
        # Generate signals
        signal = generate_signals(ticker, stock_data, news)
        cache_data(cache_key, signal, expiry_minutes=10)
        return signal
    except Exception as e:
        logger.error(f"Error generating signals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= VOLUME ANALYSIS ENDPOINTS =============

@app.get("/volume-analysis/{ticker}")
async def get_volume_analysis(ticker: str):
    """Get detailed volume analysis for a stock."""
    try:
        stock_data = get_stock_data(ticker)
        if stock_data is None:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
        
        volume_analysis = analyze_volume(stock_data)
        volume_signal = compute_volume_signal(stock_data)
        
        return {
            "ticker": ticker,
            "volume_analysis": volume_analysis,
            "volume_signal": volume_signal,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Volume analysis error for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Volume analysis failed: {str(e)}")

# ============= AI ASSISTANT ENDPOINTS =============

@app.get("/ask")
async def ask_ai_assistant_endpoint(
    q: str = Query(..., description="Your question for the AI assistant"),
    ticker: str = Query("RELIANCE.NS", description="Stock ticker for context")
):
    """AI-powered stock analysis assistant."""
    try:
        # Gather comprehensive context
        context = await _build_context(ticker)
        
        # Mock backtest data (replace with real backtesting results)
        backtest = {
            "accuracy": "73% (last 6 months)",
            "win_rate": "65% on NIFTY50 signals", 
            "avg_gain": "1.8% per trade",
            "total_trades": 150,
            "max_drawdown": "-2.3%"
        }
        
        # Get AI response
        answer = ask_ai_assistant(q, context=context, backtest=backtest)
        
        return {
            "question": q,
            "ticker": ticker,
            "answer": answer,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"AI Assistant error: {str(e)}")
        return {
            "question": q,
            "answer": f"I'm experiencing technical difficulties: {str(e)}",
            "error": True
        }

@app.get("/ask/templates")
async def get_query_templates():
    """Get predefined query templates for common questions."""
    return {
        "buy_sell": "Should I buy, sell, or hold {ticker} right now?",
        "risk_assessment": "What are the risks of investing in {ticker}?",
        "price_target": "What could be a realistic price target for {ticker}?",
        "volume_analysis": "How should I interpret the current volume pattern in {ticker}?",
        "news_impact": "How might recent news affect {ticker}'s stock price?"
    }

# ============= ENHANCED ANALYSIS ENDPOINTS =============

@app.get("/analysis/{ticker}")
async def get_enhanced_analysis_endpoint(ticker: str):
    """Get comprehensive enhanced analysis for a ticker."""
    try:
        analysis = get_enhanced_analysis(ticker)
        if analysis:
            comprehensive_analysis = analysis.get_comprehensive_analysis()
            return comprehensive_analysis
        else:
            raise HTTPException(status_code=404, detail=f"Could not get enhanced analysis for {ticker}")
    except Exception as e:
        logger.error(f"Enhanced analysis error for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Enhanced analysis failed: {str(e)}")

@app.get("/analyst/{ticker}")
async def get_analyst_data(ticker: str):
    """Get analyst recommendations and price targets for a ticker."""
    try:
        analyst_data = get_analyst_summary(ticker)
        if 'error' in analyst_data:
            raise HTTPException(status_code=404, detail=analyst_data['error'])
        return analyst_data
    except Exception as e:
        logger.error(f"Analyst data error for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analyst data failed: {str(e)}")

@app.get("/earnings/{ticker}")
async def get_earnings_data(ticker: str):
    """Get earnings estimates and history for a ticker."""
    try:
        earnings_data = get_earnings_estimates(ticker)
        if 'error' in earnings_data:
            raise HTTPException(status_code=404, detail=earnings_data['error'])
        return earnings_data
    except Exception as e:
        logger.error(f"Earnings data error for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Earnings data failed: {str(e)}")

# ============= DOMAIN ENDPOINTS =============

@app.get("/sectors")
async def get_all_sectors() -> List[SectorData]:
    """Get all available financial sectors."""
    try:
        sectors = domain_service.get_all_sectors()
        return sectors
    except Exception as e:
        logger.error(f"Error fetching sectors: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch sectors: {str(e)}")

@app.get("/sectors/{sector_key}")
async def get_sector(sector_key: str) -> SectorData:
    """Get specific sector data by key."""
    try:
        sector = domain_service.get_sector(sector_key)
        if not sector:
            raise HTTPException(status_code=404, detail=f"Sector '{sector_key}' not found")
        return sector
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching sector {sector_key}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch sector: {str(e)}")

@app.get("/sectors/{sector_key}/companies")
async def get_sector_companies(
    sector_key: str, 
    limit: int = Query(10, description="Number of companies to return")
) -> List[Dict]:
    """Get top companies in a specific sector."""
    try:
        companies = domain_service.get_sector_companies(sector_key, limit)
        return [company.dict() for company in companies]
    except Exception as e:
        logger.error(f"Error fetching companies for sector {sector_key}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch sector companies: {str(e)}")

@app.get("/industries")
async def get_all_industries() -> List[IndustryData]:
    """Get all available financial industries."""
    try:
        industries = domain_service.get_all_industries()
        return industries
    except Exception as e:
        logger.error(f"Error fetching industries: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch industries: {str(e)}")

@app.get("/industries/{industry_key}")
async def get_industry(industry_key: str) -> IndustryData:
    """Get specific industry data by key."""
    try:
        industry = domain_service.get_industry(industry_key)
        if not industry:
            raise HTTPException(status_code=404, detail=f"Industry '{industry_key}' not found")
        return industry
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching industry {industry_key}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch industry: {str(e)}")

@app.get("/industries/{industry_key}/companies")
async def get_industry_companies(
    industry_key: str, 
    limit: int = Query(10, description="Number of companies to return")
) -> List[Dict]:
    """Get top companies in a specific industry."""
    try:
        companies = domain_service.get_industry_companies(industry_key, limit)
        return [company.dict() for company in companies]
    except Exception as e:
        logger.error(f"Error fetching companies for industry {industry_key}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch industry companies: {str(e)}")

@app.get("/domains/search")
async def search_domains(q: str = Query(..., description="Search query for sectors and industries")):
    """Search for sectors and industries matching the query."""
    try:
        results = domain_service.search_domains(q)
        return {
            "query": q,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error searching domains: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Domain search failed: {str(e)}")

# ============= MARKET STATUS ENDPOINTS =============

@app.get("/market/status")
async def get_all_market_status():
    """Get status for all available markets."""
    try:
        all_status = market_service.get_all_market_status()
        return {
            "markets": all_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching market status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch market status: {str(e)}")

@app.get("/market/status/{market_key}")
async def get_market_status(market_key: str) -> MarketStatus:
    """Get market status for a specific market."""
    try:
        status = market_service.get_market_status(market_key)
        if not status:
            raise HTTPException(status_code=404, detail=f"Market '{market_key}' not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching market status for {market_key}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch market status: {str(e)}")

@app.get("/market/summary/{market_key}")
async def get_market_summary(market_key: str) -> MarketSummary:
    """Get market summary for a specific market."""
    try:
        summary = market_service.get_market_summary(market_key)
        if not summary:
            raise HTTPException(status_code=404, detail=f"Market summary for '{market_key}' not found")
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching market summary for {market_key}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch market summary: {str(e)}")

# ============= OWNERSHIP/HOLDERS ENDPOINTS =============

@app.get("/ownership/{ticker}")
async def get_ownership_data(ticker: str) -> OwnershipData:
    """Get comprehensive ownership data for a ticker."""
    try:
        ownership_data = holders_service.get_ownership_data(ticker)
        if not ownership_data:
            raise HTTPException(status_code=404, detail=f"Ownership data for '{ticker}' not found")
        return ownership_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching ownership data for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch ownership data: {str(e)}")

@app.get("/ownership/{ticker}/institutional")
async def get_institutional_holders(
    ticker: str, 
    limit: int = Query(10, description="Number of institutional holders to return")
) -> List[Dict]:
    """Get institutional holders for a ticker."""
    try:
        holders = holders_service.get_institutional_holders(ticker, limit)
        return holders
    except Exception as e:
        logger.error(f"Error fetching institutional holders for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch institutional holders: {str(e)}")

@app.get("/ownership/{ticker}/insider-transactions")
async def get_insider_transactions(
    ticker: str, 
    limit: int = Query(10, description="Number of insider transactions to return")
) -> List[Dict]:
    """Get insider transactions for a ticker."""
    try:
        transactions = holders_service.get_insider_transactions(ticker, limit)
        return transactions
    except Exception as e:
        logger.error(f"Error fetching insider transactions for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch insider transactions: {str(e)}")

@app.get("/ownership/{ticker}/major-holders")
async def get_major_holders_breakdown(ticker: str) -> Dict[str, Any]:
    """Get major holders breakdown for a ticker."""
    try:
        breakdown = holders_service.get_major_holders_breakdown(ticker)
        return breakdown
    except Exception as e:
        logger.error(f"Error fetching major holders breakdown for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch major holders breakdown: {str(e)}")

@app.get("/ownership/{ticker}/insider-roster")
async def get_insider_roster(
    ticker: str, 
    limit: int = Query(10, description="Number of insiders to return")
) -> List[Dict]:
    """Get insider roster for a ticker."""
    try:
        roster = holders_service.get_insider_roster(ticker, limit)
        return roster
    except Exception as e:
        logger.error(f"Error fetching insider roster for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch insider roster: {str(e)}")

# ============= FASTINFO ENDPOINTS =============

@app.get("/fastinfo/{ticker}")
async def get_fast_info(ticker: str) -> FastInfoData:
    """Get comprehensive fast info for a ticker."""
    try:
        fast_info = fastinfo_service.get_fast_info(ticker)
        if not fast_info:
            raise HTTPException(status_code=404, detail=f"Fast info for '{ticker}' not found")
        return fast_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching fast info for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch fast info: {str(e)}")

@app.get("/fastinfo/{ticker}/price-summary")
async def get_price_summary(ticker: str) -> Dict[str, Any]:
    """Get price summary for a ticker."""
    try:
        summary = fastinfo_service.get_price_summary(ticker)
        if not summary:
            raise HTTPException(status_code=404, detail=f"Price summary for '{ticker}' not found")
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching price summary for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch price summary: {str(e)}")

@app.get("/fastinfo/{ticker}/technical-indicators")
async def get_technical_indicators(ticker: str) -> Dict[str, Any]:
    """Get technical indicators for a ticker."""
    try:
        indicators = fastinfo_service.get_technical_indicators(ticker)
        if not indicators:
            raise HTTPException(status_code=404, detail=f"Technical indicators for '{ticker}' not found")
        return indicators
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching technical indicators for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch technical indicators: {str(e)}")

@app.get("/fastinfo/{ticker}/market-cap")
async def get_market_cap_info(ticker: str) -> Dict[str, Any]:
    """Get market cap information for a ticker."""
    try:
        market_cap_info = fastinfo_service.get_market_cap_info(ticker)
        if not market_cap_info:
            raise HTTPException(status_code=404, detail=f"Market cap info for '{ticker}' not found")
        return market_cap_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching market cap info for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch market cap info: {str(e)}")

# ============= QUOTE ENDPOINTS =============

@app.get("/quote/{ticker}")
async def get_quote_info(ticker: str) -> QuoteData:
    """Get comprehensive quote info for a ticker."""
    try:
        quote_info = quote_service.get_quote_info(ticker)
        if not quote_info:
            raise HTTPException(status_code=404, detail=f"Quote info for '{ticker}' not found")
        return quote_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching quote info for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch quote info: {str(e)}")

@app.get("/quote/{ticker}/sustainability")
async def get_sustainability_data(ticker: str) -> SustainabilityData:
    """Get sustainability data for a ticker."""
    try:
        sustainability = quote_service.get_sustainability_data(ticker)
        if not sustainability:
            raise HTTPException(status_code=404, detail=f"Sustainability data for '{ticker}' not found")
        return sustainability
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching sustainability data for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch sustainability data: {str(e)}")

@app.get("/quote/{ticker}/recommendations")
async def get_recommendations(ticker: str) -> RecommendationData:
    """Get analyst recommendations for a ticker."""
    try:
        recommendations = quote_service.get_recommendations(ticker)
        if not recommendations:
            raise HTTPException(status_code=404, detail=f"Recommendations for '{ticker}' not found")
        return recommendations
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching recommendations for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch recommendations: {str(e)}")

@app.get("/quote/{ticker}/upgrades-downgrades")
async def get_upgrades_downgrades(ticker: str) -> List[Dict[str, Any]]:
    """Get upgrades/downgrades for a ticker."""
    try:
        upgrades_downgrades = quote_service.get_upgrades_downgrades(ticker)
        return upgrades_downgrades
    except Exception as e:
        logger.error(f"Error fetching upgrades/downgrades for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch upgrades/downgrades: {str(e)}")

@app.get("/quote/{ticker}/calendar")
async def get_calendar_events(ticker: str) -> CalendarData:
    """Get calendar events for a ticker."""
    try:
        calendar = quote_service.get_calendar_events(ticker)
        if not calendar:
            raise HTTPException(status_code=404, detail=f"Calendar events for '{ticker}' not found")
        return calendar
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching calendar events for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch calendar events: {str(e)}")

@app.get("/quote/{ticker}/company-info")
async def get_company_info(ticker: str) -> Dict[str, Any]:
    """Get basic company information for a ticker."""
    try:
        company_info = quote_service.get_company_info(ticker)
        if not company_info:
            raise HTTPException(status_code=404, detail=f"Company info for '{ticker}' not found")
        return company_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching company info for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch company info: {str(e)}")

@app.get("/quote/{ticker}/sec-filings")
async def get_sec_filings(ticker: str) -> List[Dict[str, Any]]:
    """Get SEC filings for a ticker."""
    try:
        sec_filings = quote_service.get_sec_filings(ticker)
        return sec_filings
    except Exception as e:
        logger.error(f"Error fetching SEC filings for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch SEC filings: {str(e)}")

# ============= QUERY BUILDER ENDPOINTS =============

@app.get("/query-builder/fields")
async def get_query_fields(query_type: str = Query("equity", description="Type of query: equity or fund")):
    """Get available fields for query building."""
    try:
        fields = query_builder_service.get_available_fields(query_type)
        return {
            "query_type": query_type,
            "fields": fields,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching query fields: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch query fields: {str(e)}")

@app.get("/query-builder/values")
async def get_query_values(query_type: str = Query("equity", description="Type of query: equity or fund")):
    """Get available values for query building."""
    try:
        values = query_builder_service.get_available_values(query_type)
        return {
            "query_type": query_type,
            "values": values,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching query values: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch query values: {str(e)}")

@app.post("/query-builder/validate")
async def validate_query(query_data: Dict[str, Any]):
    """Validate a query structure."""
    try:
        query_type = query_data.get("query_type", "equity")
        query_dict = query_data.get("query", {})
        
        is_valid = query_builder_service.validate_query(query_dict, query_type)
        
        return {
            "valid": is_valid,
            "query_type": query_type,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error validating query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to validate query: {str(e)}")

@app.post("/query-builder/execute/equity")
async def execute_equity_query(
    query_data: Dict[str, Any],
    limit: int = Query(50, description="Maximum number of results to return")
):
    """Execute an equity query and return matching stocks."""
    try:
        query_dict = query_data.get("query", {})
        results = query_builder_service.execute_equity_query(query_dict, limit)
        
        return {
            "query": query_dict,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error executing equity query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to execute equity query: {str(e)}")

@app.post("/query-builder/execute/fund")
async def execute_fund_query(
    query_data: Dict[str, Any],
    limit: int = Query(50, description="Maximum number of results to return")
):
    """Execute a fund query and return matching funds."""
    try:
        query_dict = query_data.get("query", {})
        results = query_builder_service.execute_fund_query(query_dict, limit)
        
        return {
            "query": query_dict,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error executing fund query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to execute fund query: {str(e)}")

@app.get("/query-builder/predefined")
async def get_predefined_queries():
    """Get predefined query templates."""
    try:
        queries = query_builder_service.get_predefined_queries()
        return {
            "queries": queries,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching predefined queries: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch predefined queries: {str(e)}")

# ============= ENHANCED YFINANCE ENDPOINTS =============

@app.post("/enhanced-download")
async def enhanced_download(
    tickers: List[str] = Query(..., description="List of ticker symbols"),
    start: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    period: str = Query("1mo", description="Period: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max"),
    interval: str = Query("1d", description="Interval: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo"),
    include_indicators: bool = Query(True, description="Include technical indicators"),
    include_sentiment: bool = Query(False, description="Include sentiment analysis"),
    threads: bool = Query(True, description="Use multi-threading"),
    timeout: int = Query(30, description="Request timeout in seconds")
):
    """Enhanced download with technical indicators and sentiment analysis."""
    try:
        data = await enhanced_downloader.download_enhanced(
            tickers=tickers,
            start=start,
            end=end,
            period=period,
            interval=interval,
            include_indicators=include_indicators,
            include_sentiment=include_sentiment,
            threads=threads,
            timeout=timeout
        )
        
        if data is None or data.empty:
            raise HTTPException(status_code=404, detail="No data found for the specified tickers")
        
        return {
            "tickers": tickers,
            "data": data.to_dict('records') if not isinstance(data.columns, pd.MultiIndex) else data.to_dict(),
            "columns": list(data.columns) if not isinstance(data.columns, pd.MultiIndex) else [str(col) for col in data.columns],
            "shape": data.shape,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in enhanced download: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Enhanced download failed: {str(e)}")

@app.post("/bulk-download")
async def bulk_download(
    ticker_groups: Dict[str, List[str]] = Body(..., description="Dictionary of ticker groups"),
    period: str = Query("1mo", description="Period for all groups"),
    interval: str = Query("1d", description="Interval for all groups"),
    include_indicators: bool = Query(True, description="Include technical indicators"),
    include_sentiment: bool = Query(False, description="Include sentiment analysis")
):
    """Download data for multiple groups of tickers."""
    try:
        results = await enhanced_downloader.download_bulk_enhanced(
            ticker_groups=ticker_groups,
            period=period,
            interval=interval,
            include_indicators=include_indicators,
            include_sentiment=include_sentiment
        )
        
        return {
            "groups": list(ticker_groups.keys()),
            "results": {group: data.to_dict('records') if data is not None and not data.empty else None 
                       for group, data in results.items()},
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in bulk download: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bulk download failed: {str(e)}")

@app.get("/market-summary")
async def get_market_summary(
    tickers: List[str] = Query(..., description="List of ticker symbols for summary")
):
    """Get market summary for a list of tickers."""
    try:
        summary = enhanced_downloader.get_market_summary(tickers)
        return summary
    except Exception as e:
        logger.error(f"Error getting market summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Market summary failed: {str(e)}")

@app.get("/enhanced-download/indicators/{ticker}")
async def get_technical_indicators(
    ticker: str,
    period: str = Query("1mo", description="Period for data"),
    interval: str = Query("1d", description="Interval for data")
):
    """Get technical indicators for a specific ticker."""
    try:
        data = await enhanced_downloader.download_enhanced(
            tickers=[ticker],
            period=period,
            interval=interval,
            include_indicators=True,
            include_sentiment=False
        )
        
        if data is None or data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
        
        # Extract only technical indicator columns
        indicator_columns = [col for col in data.columns if any(indicator in str(col).upper() 
                          for indicator in ['RSI', 'MACD', 'BBU', 'BBL', 'BBM', 'SMA', 'EMA'])]
        
        if not indicator_columns:
            raise HTTPException(status_code=404, detail=f"No technical indicators found for {ticker}")
        
        indicators_data = data[indicator_columns].dropna()
        
        return {
            "ticker": ticker,
            "indicators": indicators_data.to_dict('records'),
            "columns": indicator_columns,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting technical indicators for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get technical indicators: {str(e)}")

# ============= DASHBOARD ENDPOINTS =============

@app.get("/dashboard")
async def get_dashboard(
    tickers: str = Query("AAPL,MSFT,GOOGL,AMZN,TSLA", description="Comma-separated ticker symbols"),
    news_limit: int = Query(5, description="Number of news items to return")
) -> DashboardResponse:
    """Enhanced dashboard endpoint with volume analysis, caching, and parallel processing."""
    try:
        cache_key = f"dashboard_{tickers}_{news_limit}"
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        ticker_list = [t.strip() for t in tickers.split(",")]
        
        # Fetch data in parallel
        import asyncio
        stock_tasks = [get_stock_data(ticker) for ticker in ticker_list]
        news_task = get_financial_news(news_limit)
        
        try:
            stocks, news = await asyncio.gather(
                asyncio.gather(*stock_tasks),
                news_task
            )
            stocks = list(stocks)  # Unpack the result of asyncio.gather(*stock_tasks)
        except Exception as e:
            logger.error(f"Error in parallel data fetching: {str(e)}")
            # Fallback: fetch data sequentially
            stocks = []
            for ticker in ticker_list:
                try:
                    stock_data = await get_stock_data(ticker)
                    stocks.append(stock_data)
                except Exception as stock_error:
                    logger.warning(f"Failed to fetch {ticker}: {str(stock_error)}")
                    continue
            
            try:
                news = await get_financial_news(news_limit)
            except Exception as news_error:
                logger.warning(f"Failed to fetch news: {str(news_error)}")
                news = []
        
        # Generate signals for each stock
        signals = []
        for stock in stocks:
            signal = generate_signals(stock.ticker, stock, news)
            signals.append(signal)
        
        response = DashboardResponse(
            stocks=stocks,
            news=news,
            signals=signals,
            timestamp=datetime.now().isoformat()
        )
        
        cache_data(cache_key, response, expiry_minutes=5)
        return response
        
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bulk-analysis")
async def get_bulk_analysis(tickers: str = Query("RELIANCE.NS,TCS.NS,HDFCBANK.NS", description="Comma-separated tickers")):
    """Get comprehensive analysis for multiple stocks."""
    try:
        ticker_list = [t.strip() for t in tickers.split(",")]
        results = {}
        
        for ticker in ticker_list:
            try:
                context = await _build_context(ticker)
                
                # Generate AI summary
                summary_query = f"Give me a brief analysis summary for {ticker}"
                ai_summary = ask_ai_assistant(summary_query, context=context)
                
                results[ticker] = {
                    "context": context,
                    "ai_summary": ai_summary,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                results[ticker] = {"error": str(e)}
        
        return results
        
    except Exception as e:
        logger.error(f"Bulk analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bulk analysis failed: {str(e)}")

# ============= HELPER FUNCTIONS =============

async def _build_context(ticker: str) -> dict:
    """Build comprehensive context for AI assistant."""
    context = {"ticker": ticker}
    
    try:
        # Get stock data and volume analysis
        stock_data = get_stock_data(ticker)
        if stock_data is not None and not stock_data.empty:
            latest = stock_data.iloc[-1]
            previous = stock_data.iloc[-2] if len(stock_data) > 1 else latest
            
            context.update({
                "current_price": float(latest['Close']),
                "price_change": float(latest['Close'] - previous['Close']),
                "price_change_pct": float((latest['Close'] - previous['Close']) / previous['Close'] * 100),
                "volume_analysis": analyze_volume(stock_data)
            })
            
            # Add technical indicators (basic)
            if len(stock_data) >= 20:
                context["technical_indicators"] = {
                    "SMA_20": float(stock_data['Close'].rolling(20).mean().iloc[-1]),
                    "RSI_14": float(_calculate_rsi(stock_data['Close'], 14).iloc[-1]) if len(stock_data) >= 14 else None,
                    "Volume_SMA_20": float(stock_data['Volume'].rolling(20).mean().iloc[-1])
                }
        
        # Get recent news
        try:
            news = get_recent_news(ticker, limit=3)
            if news:
                context["news_headlines"] = [item.get('title', '') for item in news[:3]]
                
                # Basic sentiment analysis
                all_text = ' '.join([item.get('title', '') + ' ' + item.get('content', '') for item in news])
                if all_text.strip():
                    sentiment = analyze_sentiment(all_text)
                    context["sentiment"] = sentiment
        except Exception as e:
            logger.warning(f"News context failed for {ticker}: {str(e)}")
        
        # Get live quote
        try:
            live_quote = get_live_quote(ticker)
            if live_quote and 'nse_live' in live_quote:
                nse_data = live_quote['nse_live']
                context.update({
                    "live_price": nse_data.get('lastPrice'),
                    "day_high": nse_data.get('dayHigh'),
                    "day_low": nse_data.get('dayLow'),
                    "live_volume": nse_data.get('totalTradedVolume')
                })
        except Exception as e:
            logger.warning(f"Live quote context failed for {ticker}: {str(e)}")
        
        # Add domain analysis context
        try:
            # Try to determine sector/industry for the ticker
            domain_context = _get_domain_context(ticker)
            if domain_context:
                context["domain_analysis"] = domain_context
        except Exception as e:
            logger.warning(f"Domain context failed for {ticker}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error building context for {ticker}: {str(e)}")
        context["context_error"] = str(e)
    
    return context

def _get_domain_context(ticker: str) -> dict:
    """Get domain context for a ticker (sector/industry analysis)"""
    try:
        # Simple mapping of tickers to sectors/industries
        ticker_sector_map = {
            'RELIANCE.NS': 'energy',
            'TCS.NS': 'technology', 
            'HDFCBANK.NS': 'finance',
            'INFY.NS': 'technology',
            'ICICIBANK.NS': 'finance',
            'WIPRO.NS': 'technology',
            'HCLTECH.NS': 'technology',
            'TECHM.NS': 'technology',
            'SUNPHARMA.NS': 'healthcare',
            'DRREDDY.NS': 'healthcare',
            'CIPLA.NS': 'healthcare',
            'ITC.NS': 'consumer',
            'HINDUNILVR.NS': 'consumer',
            'MARUTI.NS': 'consumer',
            'TITAN.NS': 'consumer',
            'BAJAJ-AUTO.NS': 'consumer',
            'TATAMOTORS.NS': 'consumer',
            'M&M.NS': 'consumer',
            'HEROMOTOCO.NS': 'consumer',
            'EICHERMOT.NS': 'consumer',
            'ONGC.NS': 'energy',
            'COALINDIA.NS': 'energy',
            'IOC.NS': 'energy',
            'BPCL.NS': 'energy',
            'POWERGRID.NS': 'utilities',
            'NTPC.NS': 'utilities',
            'SBIN.NS': 'finance',
            'AXISBANK.NS': 'finance',
            'KOTAKBANK.NS': 'finance',
            'INDUSINDBK.NS': 'finance',
            'BAJFINANCE.NS': 'finance',
            'BHARTIARTL.NS': 'communication',
            'JSWSTEEL.NS': 'materials',
            'TATASTEEL.NS': 'materials',
            'HINDALCO.NS': 'materials',
            'ULTRACEMCO.NS': 'materials',
            'SHREECEM.NS': 'materials',
            'GRASIM.NS': 'materials',
            'ADANIPORTS.NS': 'industrial',
            'LT.NS': 'industrial',
            'ASIANPAINT.NS': 'materials',
            'NESTLEIND.NS': 'consumer',
            'BRITANNIA.NS': 'consumer',
            'DIVISLAB.NS': 'healthcare',
            'UPL.NS': 'materials',
            'DLF.NS': 'real_estate'
        }
        
        # Get sector for ticker
        sector_key = ticker_sector_map.get(ticker.upper())
        if sector_key:
            sector_data = domain_service.get_sector(sector_key)
            if sector_data:
                return {
                    "sector": {
                        "name": sector_data.name,
                        "key": sector_data.key,
                        "overview": sector_data.overview.dict(),
                        "top_companies": [company.dict() for company in sector_data.top_companies[:5]]
                    }
                }
        
        return None
        
    except Exception as e:
        logger.warning(f"Error getting domain context for {ticker}: {str(e)}")
        return None

def _calculate_rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    """Calculate RSI indicator."""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

# ============= ERROR HANDLERS =============

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main_combined:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
