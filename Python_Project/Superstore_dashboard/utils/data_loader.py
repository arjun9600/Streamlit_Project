import os
import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    file_path = os.path.join(project_root, "data", "Sample - Superstore.csv")

    df = pd.read_csv(file_path, encoding="utf-8")
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    df['Shipping Days'] = (df['Ship Date'] - df['Order Date']).dt.days
    df['Margin %'] = (df['Profit'] / df['Sales']) * 100
    return df

def apply_custom_theme():
    """Vivid Neon theme — near-black canvas with neon green / mint cyan /
    sky blue / electric purple / deep magenta accents."""
    st.markdown("""
        <style>
        :root {
            --neon-green: #14e81e;
            --mint-cyan: #00ea8d;
            --sky-blue: #017ed5;
            --electric-purple: #b53dff;
            --deep-magenta: #8d00c4;
            --ink: #E9FBEA;
        }

        .stApp {
            background: radial-gradient(circle at 15% 0%, rgba(141,0,196,0.25) 0%, transparent 45%),
                        radial-gradient(circle at 85% 100%, rgba(1,126,213,0.20) 0%, transparent 45%),
                        linear-gradient(160deg, #07080d 0%, #0a0614 45%, #050608 100%);
            color: var(--ink);
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a0330 0%, #06070d 100%);
            border-right: 1px solid var(--electric-purple);
        }
        section[data-testid="stSidebar"] * { color: var(--ink) !important; }

        h1, h2, h3, h4 {
            color: var(--mint-cyan) !important;
            font-weight: 800 !important;
            letter-spacing: -0.01em;
            text-shadow: 0 0 18px rgba(0,234,141,0.35);
        }
        p, span, label, .stCaption, .stMarkdown { color: var(--ink); }

        div[data-testid="stMetric"] {
            background: rgba(181, 61, 255, 0.10);
            border: 1px solid var(--electric-purple);
            border-radius: 14px;
            padding: 18px;
            box-shadow: 0 0 22px rgba(181, 61, 255, 0.25);
            transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        }
        div[data-testid="stMetric"]:hover {
            border-color: var(--neon-green);
            box-shadow: 0 0 28px rgba(20, 232, 30, 0.35);
            transform: translateY(-2px);
        }
        div[data-testid="stMetricLabel"] {
            color: var(--sky-blue) !important;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.75rem;
        }
        div[data-testid="stMetricValue"] {
            color: var(--neon-green) !important;
            font-weight: 800;
            font-size: 1.9rem;
            text-shadow: 0 0 16px rgba(20, 232, 30, 0.55);
        }

        .stButton > button {
            background: linear-gradient(135deg, var(--electric-purple), var(--deep-magenta));
            color: #ffffff;
            border: 1px solid var(--mint-cyan);
            border-radius: 10px;
            font-weight: 700;
            padding: 0.5rem 1rem;
            transition: box-shadow 0.2s ease, border-color 0.2s ease;
        }
        .stButton > button:hover {
            border-color: var(--neon-green);
            box-shadow: 0 0 18px rgba(20, 232, 30, 0.6);
            color: #ffffff;
        }

        div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"] {
            background-color: rgba(26, 3, 48, 0.65) !important;
            border: 1px solid var(--electric-purple) !important;
            border-radius: 8px !important;
        }
        input, textarea { color: var(--ink) !important; }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--sky-blue);
            border-radius: 10px;
            overflow: hidden;
        }

        hr { border-color: var(--electric-purple) !important; }

        /* Business insight cards */
        .insight-box {
            background: linear-gradient(135deg, rgba(20,232,30,0.08), rgba(1,126,213,0.06));
            border: 1px solid var(--mint-cyan);
            border-left: 4px solid var(--neon-green);
            border-radius: 12px;
            padding: 16px 20px;
            margin-top: 8px;
            margin-bottom: 6px;
            box-shadow: 0 0 20px rgba(20,232,30,0.15);
        }
        .insight-title {
            color: var(--neon-green);
            font-weight: 800;
            font-size: 1rem;
            text-shadow: 0 0 10px rgba(20,232,30,0.5);
        }
        .insight-subtitle {
            color: var(--sky-blue);
            font-size: 0.8rem;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .insight-box ul { margin: 0; padding-left: 1.2rem; }
        .insight-box li { color: var(--ink); font-size: 0.9rem; margin-bottom: 5px; line-height: 1.4; }
        </style>
    """, unsafe_allow_html=True)
