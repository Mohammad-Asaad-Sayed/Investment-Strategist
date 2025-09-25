import os
import yfinance as yf
from agno.agent import Agent
from agno.models.groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Data Fetching ---
def compare_stocks(symbols):
    """Fetch 6-month % change for each stock symbol."""
    data = yf.download(symbols, period="6mo")['Close']
    return {symbol: data[symbol].pct_change().sum() for symbol in symbols}

def get_company_info(symbol):
    """Fetch company fundamentals (name, sector, market cap, summary)."""
    stock = yf.Ticker(symbol)
    return {
        "name": stock.info.get("longName", "N/A"),
        "sector": stock.info.get("sector", "N/A"),
        "market_cap": stock.info.get("marketCap", "N/A"),
        "summary": stock.info.get("longBusinessSummary", "N/A"),
        "pe_ratio": stock.info.get("trailingPE", "N/A"),
        "dividend_yield": stock.info.get("dividendYield", "N/A"),
    }

def get_company_news(symbol):
    """Fetch latest 5 news articles for a stock."""
    stock = yf.Ticker(symbol)
    return stock.news[:5]

# --- Agent Definitions (using Groq models) ---
market_analyst = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),  # Strong for market analysis
    description="Analyzes stock performance trends.",
    instructions=[
        "Compare stock performance over 6 months.",
        "Rank stocks by % change and volatility.",
    ],
    markdown=True
)

company_researcher = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),  # Balanced model for research
    description="Fetches company profiles and news.",
    instructions=[
        "Summarize company fundamentals (sector, market cap, P/E ratio).",
        "Highlight key news impacting stock price.",
    ],
    markdown=True
)

stock_strategist = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),  # Larger model for reasoning
    description="Provides investment recommendations.",
    instructions=[
        "Evaluate risk-reward based on performance and news.",
        "Recommend top 3 stocks with justification.",
    ],
    markdown=True
)

team_lead = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),  # Best for compiling final reports
    description="Compiles final investment report.",
    instructions=[
        "Combine market analysis, company data, and recommendations.",
        "Rank stocks in ascending order of investment potential.",
    ],
    markdown=True
)

# --- Core Functions ---
def get_market_analysis(symbols):
    """Generate performance comparison report."""
    performance_data = compare_stocks(symbols)
    if not performance_data:
        return "No valid data found."
    return market_analyst.run(f"Compare: {performance_data}").content

def get_company_analysis(symbol):
    """Generate company profile and news summary."""
    info = get_company_info(symbol)
    news = get_company_news(symbol)
    return company_researcher.run(
        f"Analyze {info['name']} ({symbol}):\n"
        f"Sector: {info['sector']}\n"
        f"Market Cap: ${info['market_cap']:,}\n"
        f"P/E Ratio: {info['pe_ratio']}\n"
        f"News: {news}"
    ).content

def get_stock_recommendations(symbols):
    """Generate top stock picks."""
    market_data = get_market_analysis(symbols)
    company_data = {s: get_company_analysis(s) for s in symbols}
    return stock_strategist.run(
        f"Market Analysis:\n{market_data}\n\n"
        f"Company Data:\n{company_data}\n\n"
        "Recommend top 3 stocks:"
    ).content

def get_final_report(symbols):
    """Compile full investment report."""
    market_analysis = get_market_analysis(symbols)
    company_analyses = {s: get_company_analysis(s) for s in symbols}
    recommendations = get_stock_recommendations(symbols)
    return team_lead.run(
        f"Market Analysis:\n{market_analysis}\n\n"
        f"Company Profiles:\n{company_analyses}\n\n"
        f"Recommendations:\n{recommendations}\n\n"
        "Generate a ranked list of stocks to buy (ascending order)."
    ).content
