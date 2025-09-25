import streamlit as st
from main import get_final_report
import plotly.graph_objects as go
import yfinance as yf

# --- Page Config ---
st.set_page_config(page_title="AI Investment Strategist", page_icon="📈", layout="wide")

# Custom CSS for cards
st.markdown("""
    <style>
        .report-box {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #4CAF50;">📈 AI Investment Strategist</h1>
        <h4 style="color: #6c757d;">Personalized investment reports with the latest AI-powered insights</h4>
    </div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("### ⚙️ Configuration")
input_symbols = st.sidebar.text_input("Enter Stock Symbols (comma-separated)", "AAPL, TSLA, GOOG")
api_key = st.sidebar.text_input("Google API Key (optional)", type="password")
generate = st.sidebar.button("🚀 Generate Report")

stocks_symbols = [s.strip().upper() for s in input_symbols.split(",") if s.strip()]

# Generate report
if generate:
    if not stocks_symbols:
        st.error("❌ Please enter at least one stock symbol.")
    elif not api_key:
        st.warning("⚠️ API key missing. Some features may not work.")
    else:
        with st.spinner("🤖 Generating investment report..."):
            report = get_final_report(stocks_symbols)

        # Layout: Report | Chart
        col1, col2 = st.columns([1.4, 1])

        with col1:
            st.subheader("📄 Investment Report")
            #st.markdown(f"<div class='report-box'>{report}</div>", unsafe_allow_html=True)
            st.info("This report combines market performance, company insights, and AI recommendations.")

        with col2:
            st.subheader("📊 Stock Performance (6 Months)")
            stock_data = yf.download(stocks_symbols, period="6mo")['Close']
            fig = go.Figure()
            for symbol in stocks_symbols:
                fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data[symbol], mode='lines', name=symbol))
            fig.update_layout(
                title="Stock Prices Over 6 Months",
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)