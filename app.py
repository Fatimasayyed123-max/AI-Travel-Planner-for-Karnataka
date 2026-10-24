"""
YatraSaathi AI — Karnataka Smart Travel Planner
National Hackathon Edition | Version 4.0 (Full Integration)

A comprehensive, travel-tech AI companion for Karnataka tourism featuring:
- Emerald green, deep navy, warm cream & white luxury visual palette
- Dynamic AI-generated itineraries using Google Gemini (gemini-3.8-flash)
- Smart Budget Optimizer with transport, accommodation, food, and activities breakdown
- SafeRoute AI with real-time weather risk advisories, travel precautions & helplines
- Real-time Adaptive Replanning ('My Plan Changed') with side-by-side comparison & restore
- Kannada Buddy AI: Smart Travel Translator & Audio Phrasebook (English, Hindi, Marathi, Kannada)
- Heritage Storyteller AI: Historical stories, UNESCO World Heritage monuments & interactive Q&A
- Permanent .env configuration & secure credential management
"""

import os
import re
import json
import time
import base64
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from groq import Groq
import groq

# Load environment variables from .env file
load_dotenv()


# ==========================================
# 1. PAGE CONFIGURATION & METADATA
# ==========================================
st.set_page_config(
    page_title="YatraSaathi AI — Discover Karnataka, Your Way",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Recommended Groq Model (High-Speed Open-Weight Reasoning Model: 131k context, ~500 T/s)
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
FALLBACK_GROQ_MODEL = "openai/gpt-oss-20b"
DEFAULT_GEMINI_MODEL = DEFAULT_GROQ_MODEL  # Backward compatibility alias


# ==========================================
# 2. LOCAL ASSET HELPERS
# ==========================================
def get_hero_image_b64() -> str:
    """Loads the local Karnataka hero image as base64 for background embedding."""
    hero_path = os.path.join(os.path.dirname(__file__), "assets", "karnataka_hero.jpg")
    if os.path.exists(hero_path):
        try:
            with open(hero_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            pass
    return ""

HERO_B64 = get_hero_image_b64()


# ==========================================
# 3. PREMIUM CSS STYLING
# ==========================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }}

    /* 1. Main Page Canvas Background: Midnight Navy to Deep Emerald */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {{
        background: linear-gradient(175deg, #071B1A 0%, #0A2624 35%, #0B302B 70%, #071B1A 100%) fixed !important;
        color: #D1D5DB !important;
    }}
    .main {{
        background: transparent !important;
    }}
    [data-testid="stSidebar"] {{
        background: #051615 !important;
        border-right: 1px solid #28564C !important;
    }}
    [data-testid="stSidebar"] * {{
        color: #D1D5DB;
    }}
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {{
        color: #F8F4E8 !important;
    }}

    /* 2. Top Navigation Bar */
    .top-navbar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(11, 48, 43, 0.95);
        backdrop-filter: blur(14px);
        padding: 0.9rem 1.8rem;
        border-radius: 18px;
        box-shadow: 0 8px 24px rgba(7, 27, 26, 0.45);
        border: 1px solid #28564C;
        margin-bottom: 1.4rem;
    }}
    .brand-logo {{
        display: flex;
        align-items: center;
        gap: 0.8rem;
        text-decoration: none;
    }}
    .brand-icon {{
        width: 42px;
        height: 42px;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.35);
    }}
    .brand-title {{
        font-family: 'Outfit', sans-serif;
        font-size: 1.45rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #F8F4E8 !important;
    }}
    .brand-subtitle {{
        font-size: 0.78rem;
        font-weight: 700;
        color: #D6B46A !important; /* Soft gold */
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }}
    .nav-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        background: rgba(16, 185, 129, 0.12);
        color: #10B981 !important;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
        border: 1px solid #28564C;
    }}

    /* 3. Hero Section */
    .hero-container {{
        position: relative;
        border-radius: 24px;
        padding: 3.5rem 3rem;
        background: linear-gradient(135deg, rgba(7, 27, 26, 0.92) 0%, rgba(11, 48, 43, 0.88) 100%),
                    url('data:image/jpeg;base64,{HERO_B64}') center/cover no-repeat;
        color: #D1D5DB;
        box-shadow: 0 20px 40px rgba(7, 27, 26, 0.5);
        margin-bottom: 2.2rem;
        overflow: hidden;
        border: 1px solid #28564C;
    }}
    .hero-pill {{
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(214, 180, 106, 0.15);
        backdrop-filter: blur(8px);
        padding: 6px 16px;
        border-radius: 30px;
        font-size: 0.86rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        color: #D6B46A; /* Soft gold */
        border: 1px solid rgba(214, 180, 106, 0.35);
        margin-bottom: 1.2rem;
    }}
    .hero-heading {{
        font-family: 'Outfit', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        line-height: 1.15;
        letter-spacing: -0.8px;
        color: #F8F4E8; /* Warm cream */
        margin-bottom: 0.8rem;
        text-shadow: 0 2px 12px rgba(0, 0, 0, 0.5);
    }}
    .hero-subheading {{
        font-size: 1.25rem;
        font-weight: 400;
        color: #D1D5DB; /* Light gray */
        max-width: 760px;
        line-height: 1.6;
        margin-bottom: 1.8rem;
    }}
    .hero-features {{
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-top: 1.8rem;
        padding-top: 1.6rem;
        border-top: 1px solid rgba(40, 86, 76, 0.5);
    }}
    .feature-pill {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
        font-weight: 600;
        color: #F8F4E8;
        background: rgba(11, 48, 43, 0.75);
        padding: 7px 16px;
        border-radius: 20px;
        border: 1px solid #28564C;
    }}

    /* 4. Section Headers */
    .section-title-wrap {{
        margin-top: 2.2rem;
        margin-bottom: 1.4rem;
    }}
    .section-eyebrow {{
        font-size: 0.84rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #10B981 !important; /* Primary accent: emerald green */
        margin-bottom: 0.35rem;
    }}
    .section-title {{
        font-family: 'Outfit', sans-serif;
        font-size: 2.15rem;
        font-weight: 800;
        color: #F8F4E8 !important; /* Main headings: warm cream */
        letter-spacing: -0.5px;
        line-height: 1.25;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
    }}
    .section-desc {{
        font-size: 1.02rem;
        color: #D1D5DB !important; /* Body/supporting text: light gray */
        margin-top: 0.35rem;
        max-width: 820px;
        line-height: 1.55;
    }}

    /* Canvas general markdown headings */
    .stMainBlockContainer h1,
    .stMainBlockContainer h2,
    .stMainBlockContainer h3,
    .stMainBlockContainer h4,
    .stMainBlockContainer h5,
    [data-testid="stMainBlockContainer"] h1,
    [data-testid="stMainBlockContainer"] h2,
    [data-testid="stMainBlockContainer"] h3,
    [data-testid="stMainBlockContainer"] h4,
    [data-testid="stMainBlockContainer"] h5 {{
        color: #F8F4E8 !important;
        font-family: 'Outfit', sans-serif;
    }}

    /* 5. Destination Cards (Explore Destinations): Warm Cream Surface with Deep Navy Text */
    .dest-card-container {{
        background: #F5F3EB !important; /* Light card surface: warm cream */
        border-radius: 20px;
        border: 1px solid #28564C !important; /* Subtle emerald border */
        box-shadow: 0 8px 24px rgba(7, 27, 26, 0.35);
        overflow: hidden;
        display: flex;
        flex-direction: column;
        height: 100%;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    }}
    .dest-card-container:hover {{
        transform: translateY(-5px);
        box-shadow: 0 16px 32px rgba(16, 185, 129, 0.2);
        border-color: #10B981 !important;
    }}
    .dest-image-wrap {{
        position: relative;
        height: 180px;
        overflow: hidden;
    }}
    .dest-image {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.4s ease;
    }}
    .dest-card-container:hover .dest-image {{
        transform: scale(1.05);
    }}
    .dest-tag-badge {{
        position: absolute;
        top: 12px;
        right: 12px;
        background: rgba(7, 27, 26, 0.9);
        backdrop-filter: blur(6px);
        color: #D6B46A !important; /* Soft gold */
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        border: 1px solid #28564C;
    }}
    .dest-content {{
        padding: 1.4rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        flex-grow: 1;
    }}
    .dest-name {{
        font-family: 'Outfit', sans-serif;
        font-size: 1.35rem;
        font-weight: 700;
        color: #102A2A !important; /* Text on light cards: deep navy */
        margin-bottom: 0.2rem;
    }}
    .dest-tagline {{
        font-size: 0.88rem;
        color: #10B981 !important; /* Emerald green accent */
        font-weight: 700;
        margin-bottom: 0.75rem;
    }}
    .dest-desc {{
        font-size: 0.9rem;
        color: #102A2A !important; /* Deep navy text */
        line-height: 1.5;
        margin-bottom: 1rem;
    }}
    .dest-meta-grid {{
        background: #EAE6DB !important;
        border-radius: 12px;
        padding: 0.75rem;
        font-size: 0.82rem;
        margin-top: 0.5rem;
        border: 1px solid #DDD8CB !important;
        color: #102A2A !important;
    }}
    .dest-meta-item {{
        display: flex;
        align-items: center;
        gap: 0.4rem;
        margin-bottom: 0.3rem;
        color: #102A2A !important;
    }}

    /* Smart Travel Companion Feature Cards */
    .companion-card {{
        background: #F5F3EB !important; /* Warm cream */
        border: 1px solid #28564C !important;
        border-radius: 18px;
        padding: 1.4rem;
        box-shadow: 0 4px 16px rgba(7, 27, 26, 0.25);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 200px;
        margin-bottom: 0.8rem;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    }}
    .companion-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 28px rgba(16, 185, 129, 0.2);
        border-color: #10B981 !important;
    }}
    .companion-icon {{
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }}
    .companion-title {{
        font-family: 'Outfit', sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
        color: #102A2A !important;
        margin-bottom: 0.4rem;
    }}
    .companion-desc {{
        font-size: 0.9rem;
        color: #2D3748 !important;
        line-height: 1.55;
    }}

    /* 6. Form Container Wrapper (Plan Your Bespoke Journey) */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: #0B302B !important; /* Secondary background: dark emerald */
        border: 1px solid #28564C !important; /* Subtle emerald border */
        border-radius: 20px !important;
        padding: 1.4rem !important;
        box-shadow: 0 10px 30px rgba(7, 27, 26, 0.4) !important;
    }}

    /* 7. Inputs, Dropdowns, Selectboxes & Sliders */
    .stTextInput label,
    .stSelectbox label,
    .stNumberInput label,
    .stSlider label,
    .stMultiSelect label,
    .stRadio label {{
        color: #F8F4E8 !important; /* Warm cream labels */
        font-weight: 600 !important;
    }}
    .stTextInput p,
    .stSelectbox p,
    .stNumberInput p,
    .stSlider p,
    .stMultiSelect p {{
        color: #D1D5DB !important; /* Light gray caption/help */
    }}
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    .stTextInput input,
    .stNumberInput input {{
        background-color: #F5F3EB !important; /* Warm cream input surface */
        color: #102A2A !important; /* Deep navy text */
        border: 1px solid #28564C !important; /* Subtle emerald border */
        border-radius: 10px !important;
    }}
    div[data-baseweb="select"] span {{
        color: #102A2A !important;
    }}
    div[data-baseweb="select"] svg {{
        fill: #102A2A !important;
    }}
    span[data-baseweb="tag"] {{
        background-color: #0B302B !important;
        color: #F8F4E8 !important;
        border: 1px solid #28564C !important;
    }}
    span[data-baseweb="tag"] svg {{
        fill: #F8F4E8 !important;
    }}

    /* 8. Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: #0B302B !important;
        border-radius: 12px !important;
        padding: 5px !important;
        border: 1px solid #28564C !important;
        gap: 0.5rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: #D1D5DB !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 8px 18px !important;
        border: none !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #10B981 !important; /* Emerald green accent */
        color: #071B1A !important; /* Deep navy text on active tab */
        font-weight: 700 !important;
    }}

    /* 9. Itinerary Day Timeline Cards: Warm Cream Surface */
    .itinerary-day-card {{
        background: #F5F3EB !important; /* Warm cream */
        border: 1px solid #28564C !important;
        border-radius: 16px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 16px rgba(7, 27, 26, 0.25);
        border-left: 6px solid #10B981 !important;
        transition: all 0.2s ease;
    }}
    .itinerary-day-card:hover {{
        border-left-color: #34D399 !important;
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.15);
    }}
    .day-badge-title {{
        font-family: 'Outfit', sans-serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: #102A2A !important; /* Deep navy */
        margin-bottom: 0.8rem;
    }}
    .time-slot {{
        display: flex;
        align-items: flex-start;
        gap: 0.8rem;
        margin-bottom: 0.75rem;
        font-size: 0.94rem;
        line-height: 1.55;
        color: #102A2A !important; /* Deep navy */
    }}
    .time-icon {{
        font-size: 1.1rem;
        min-width: 26px;
        text-align: center;
    }}

    /* KPI Metrics Styling */
    [data-testid="stMetric"] {{
        background-color: #0B302B !important;
        border: 1px solid #28564C !important;
        border-radius: 14px !important;
        padding: 0.9rem 1.1rem !important;
        box-shadow: 0 4px 12px rgba(7, 27, 26, 0.3) !important;
    }}
    [data-testid="stMetricLabel"] p {{
        color: #D1D5DB !important;
        font-weight: 600 !important;
    }}
    [data-testid="stMetricValue"] div {{
        color: #10B981 !important;
        font-weight: 700 !important;
    }}

    /* 10. Smart Budget Cards: Warm Cream Surface */
    .budget-card {{
        background: #F5F3EB !important; /* Warm cream */
        border: 1px solid #28564C !important;
        border-radius: 16px;
        padding: 1.25rem 1.4rem;
        box-shadow: 0 4px 14px rgba(7, 27, 26, 0.25);
        text-align: left;
    }}
    .budget-label {{
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #264642 !important; /* Deep slate on light card */
        letter-spacing: 0.5px;
        margin-bottom: 0.3rem;
    }}
    .budget-amount {{
        font-family: 'Outfit', sans-serif;
        font-size: 1.6rem;
        font-weight: 800;
        color: #102A2A !important; /* Deep navy */
        letter-spacing: -0.5px;
    }}
    .budget-share {{
        font-size: 0.82rem;
        color: #10B981 !important; /* Emerald green */
        font-weight: 700;
        margin-top: 0.2rem;
    }}

    /* 11. Adaptive Replan Cards */
    .adaptive-executive-card {{
        background: #0B302B !important; /* Dark emerald */
        border-radius: 20px;
        border: 1px solid #28564C !important;
        padding: 2rem 2.2rem;
        box-shadow: 0 10px 30px rgba(7, 27, 26, 0.4);
        margin-bottom: 2rem;
        color: #D1D5DB !important;
    }}
    .replan-col-cancelled {{
        background: rgba(239, 68, 68, 0.12) !important;
        border: 1px solid #EF4444 !important;
        border-radius: 14px;
        padding: 1.2rem;
        height: 100%;
        color: #F8F4E8 !important;
    }}
    .replan-col-adapted {{
        background: rgba(16, 185, 129, 0.12) !important;
        border: 1px solid #10B981 !important;
        border-radius: 14px;
        padding: 1.2rem;
        height: 100%;
        color: #F8F4E8 !important;
    }}

    /* 12. Kannada Buddy AI Styles */
    .kannada-badge-row {{
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: flex-end;
        gap: 0.65rem;
        margin-bottom: 0.35rem;
    }}
    @media (max-width: 768px) {{
        .kannada-badge-row {{
            justify-content: flex-start;
            margin-top: 0.4rem;
            margin-bottom: 0.75rem;
        }}
    }}
    .offline-badge, .ai-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        white-space: nowrap;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        line-height: 1.25;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .offline-badge {{
        background: rgba(16, 185, 129, 0.18) !important;
        color: #10B981 !important;
        border: 1px solid #10B981 !important;
    }}
    .ai-badge {{
        background: rgba(214, 180, 106, 0.18) !important;
        color: #D6B46A !important; /* Soft gold */
        border: 1px solid #D6B46A !important;
    }}
    .phrase-card {{
        background: #F5F3EB !important; /* Warm cream light card */
        border: 1px solid #28564C !important;
        border-radius: 14px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 2px 8px rgba(7, 27, 26, 0.2);
        transition: all 0.2s ease;
    }}
    .phrase-card:hover {{
        border-color: #10B981 !important;
        box-shadow: 0 6px 16px rgba(16, 185, 129, 0.2);
    }}
    .phrase-card .phrase-kannada {{
        color: #102A2A !important; /* Deep navy */
    }}
    .phrase-card .phrase-phonetic {{
        color: #10B981 !important; /* Emerald green */
    }}
    .phrase-card .phrase-meaning {{
        color: #102A2A !important; /* Deep navy */
    }}
    .phrase-card .phrase-tip {{
        color: #264642 !important;
    }}
    .kannada-reverse-card {{
        background: #F5F3EB !important; /* Warm cream */
        border: 1px solid #28564C !important;
        border-radius: 16px;
        padding: 1.4rem;
        margin-top: 1rem;
        box-shadow: 0 4px 14px rgba(7, 27, 26, 0.25);
        color: #102A2A !important;
    }}
    .kannada-reverse-card .reverse-trans-text {{
        color: #102A2A !important;
    }}
    .kannada-reverse-card .reverse-context-box {{
        background: #EAE6DB !important;
        color: #102A2A !important;
        border: 1px solid #DDD8CB !important;
    }}
    .kannada-reverse-card .reverse-reply-box {{
        background: #0B302B !important;
        color: #10B981 !important;
        border-left: 4px solid #10B981 !important;
    }}
    .kannada-output-card {{
        background: linear-gradient(135deg, #071B1A 0%, #0B302B 60%, #071B1A 100%) !important;
        border-radius: 18px;
        padding: 1.8rem 2rem;
        color: #F8F4E8 !important;
        box-shadow: 0 12px 28px rgba(7, 27, 26, 0.4);
        border: 1px solid #10B981 !important;
        margin-top: 1.2rem;
        margin-bottom: 1.2rem;
        position: relative;
    }}
    .kannada-script-text {{
        font-size: 2.1rem;
        font-weight: 800;
        line-height: 1.35;
        color: #F8F4E8 !important; /* Warm cream */
        margin-bottom: 0.5rem;
        letter-spacing: 0.5px;
        text-shadow: 0 2px 8px rgba(0,0,0,0.5);
    }}
    .kannada-phonetic-text {{
        font-size: 1.22rem;
        font-weight: 600;
        color: #10B981 !important; /* Emerald green */
        margin-bottom: 0.75rem;
        letter-spacing: 0.3px;
        font-style: italic;
    }}
    .kannada-meaning-text {{
        font-size: 1.05rem;
        color: #D1D5DB !important; /* Light gray */
        border-top: 1px solid #28564C !important;
        padding-top: 0.75rem;
        margin-top: 0.5rem;
    }}
    .kannada-tip-box {{
        background: #0B302B !important;
        border-left: 4px solid #10B981 !important;
        padding: 0.9rem 1.2rem;
        border-radius: 8px;
        margin-top: 1rem;
        font-size: 0.92rem;
        color: #F8F4E8 !important;
        border: 1px solid #28564C !important;
        border-left-width: 4px !important;
    }}

    /* 13. Heritage Storyteller Styles */
    .heritage-monument-card {{
        background: #F5F3EB !important; /* Warm cream */
        border: 1px solid #28564C !important;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 8px 24px rgba(7, 27, 26, 0.3);
        margin-bottom: 1.5rem;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }}
    .heritage-monument-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 16px 32px rgba(16, 185, 129, 0.2);
        border-color: #10B981 !important;
    }}
    .heritage-monument-card div {{
        color: #102A2A;
    }}
    .heritage-hero-banner {{
        background: linear-gradient(135deg, #071B1A 0%, #0B302B 60%, #071B1A 100%) !important;
        border-radius: 20px;
        padding: 2.2rem 2.5rem;
        color: #F8F4E8 !important;
        margin-bottom: 2rem;
        border: 1px solid #28564C !important;
        box-shadow: 0 12px 32px rgba(7, 27, 26, 0.4);
    }}
    .heritage-section-box {{
        background: #F5F3EB !important; /* Warm cream */
        border: 1px solid #28564C !important;
        border-radius: 16px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 14px rgba(7, 27, 26, 0.25);
        color: #102A2A !important;
    }}
    .heritage-section-box h4 {{
        color: #102A2A !important; /* Deep navy */
    }}
    .heritage-section-box p,
    .heritage-section-box div {{
        color: #102A2A !important;
    }}

    /* 14. SafeRoute AI Alert Styles: Warm Cream Surface */
    .safety-alert-card {{
        background: #F5F3EB !important; /* Warm cream */
        border-radius: 16px;
        border: 1px solid #28564C !important;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 14px rgba(7, 27, 26, 0.25);
        color: #102A2A !important;
    }}
    .safety-alert-card strong {{
        color: #102A2A !important;
    }}
    .safety-alert-card p {{
        color: #102A2A !important;
    }}
    .safety-warning-pill {{
        background: rgba(239, 68, 68, 0.15) !important;
        color: #DC2626 !important;
        border: 1px solid #EF4444 !important;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
    }}
    .safety-good-pill {{
        background: rgba(16, 185, 129, 0.15) !important;
        color: #047857 !important;
        border: 1px solid #10B981 !important;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
    }}

    /* 15. Footer */
    .footer-container {{
        background: #051615 !important;
        color: #D1D5DB !important;
        border-radius: 24px;
        padding: 2.5rem 2.5rem 1.8rem 2.5rem;
        margin-top: 3.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #28564C !important;
    }}
    .footer-brand {{
        font-family: 'Outfit', sans-serif;
        font-size: 1.4rem;
        font-weight: 800;
        color: #F8F4E8 !important;
        margin-bottom: 0.2rem;
    }}
    .footer-tagline {{
        font-size: 0.92rem;
        color: #D6B46A !important; /* Soft gold */
        font-weight: 600;
        margin-bottom: 1.2rem;
    }}
    .footer-links {{
        font-size: 0.85rem;
        color: #D1D5DB !important;
        line-height: 1.6;
    }}

    /* 16. Primary & Secondary Buttons */
    div.stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: #071B1A !important; /* Deep navy text on emerald button */
        font-weight: 800 !important;
        font-size: 1.05rem !important;
        padding: 0.65rem 1.8rem !important;
        border-radius: 12px !important;
        border: 1px solid #10B981 !important;
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.35) !important;
        transition: all 0.25s ease !important;
    }}
    div.stButton > button[kind="primary"]:hover {{
        background: linear-gradient(135deg, #34D399 0%, #10B981 100%) !important;
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.5) !important;
        transform: translateY(-2px) !important;
    }}
    div.stButton > button[kind="secondary"] {{
        border-radius: 10px !important;
        border: 1px solid #28564C !important;
        font-weight: 600 !important;
        color: #F8F4E8 !important;
        background: #0B302B !important; /* Dark emerald */
        transition: all 0.2s ease !important;
    }}
    div.stButton > button[kind="secondary"]:hover {{
        border-color: #10B981 !important;
        color: #10B981 !important;
        background: #071B1A !important;
    }}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 4. STRUCTURED DATA SCHEMAS FOR GEMINI AI
# ==========================================
class BudgetBreakdown(BaseModel):
    transport_estimate: int = Field(description="Estimated transport cost in INR for the trip (e.g. cabs, trains, fuel, local transit)")
    accommodation_estimate: int = Field(description="Estimated lodging cost in INR for the total duration")
    food_estimate: int = Field(description="Estimated meals and dining cost in INR")
    activities_estimate: int = Field(description="Estimated entry tickets, permits, safari, and activities in INR")
    notes: str = Field(description="Short guidance note regarding budget estimates")
    savings_tips: list[str] = Field(default_factory=list, description="2-3 practical ways to save money along this route")

class DayPlan(BaseModel):
    day: str = Field(description="E.g. Day 1: Heritage Arrival & Mysore Palace")
    morning: str = Field(description="Detailed morning activity, arrival notes, and sightseeing")
    afternoon: str = Field(description="Afternoon activities and local food recommendation")
    evening: str = Field(description="Evening activity, sunset viewpoint, or cultural event")

class DishRecommendation(BaseModel):
    name: str = Field(description="Name of the authentic Karnataka delicacy")
    description: str = Field(description="Short description and why travellers should try it along this route")

class ItineraryResponse(BaseModel):
    title: str = Field(description="Catchy title for this custom Karnataka itinerary")
    primary_hub: str = Field(description="Primary circuit or base destination in Karnataka (e.g. Mysuru, Hampi, Coorg, Bengaluru, Gokarna, Chikkamagaluru)")
    summary: str = Field(description="2-3 sentence overview explaining how this itinerary fulfills the user's specific starting city, budget, duration, travellers, and interests")
    estimated_cost_per_person: int = Field(description="Estimated cost per person in INR")
    days: list[DayPlan] = Field(description="Day-by-day plan with EXACTLY the requested number of days")
    must_try_dishes: list[DishRecommendation] = Field(description="4-5 authentic Karnataka delicacies along this route")
    travel_tips: list[str] = Field(description="3-4 practical travel tips for this route, transit options, and local etiquette")
    budget_breakdown: BudgetBreakdown = Field(description="Realistic breakdown of estimated costs for transport, stay, food, and activities")

class RevisedItineraryResponse(BaseModel):
    situation_summary: str = Field(description="Short summary of the disruption handled")
    ai_note: str = Field(description="Empathetic, reassuring note explaining how this substitution preserves the vacation")
    postponed_activities: list[str] = Field(description="Activities cancelled or postponed due to the disruption")
    adapted_alternatives: list[str] = Field(description="Safe, indoor, or relaxed alternatives substituted in the same area")
    revised_days: list[DayPlan] = Field(description="Complete revised day-by-day schedule incorporating the substitutions")
    revised_budget_notes: str = Field(default="", description="Any cost adjustment or savings notes due to substitutions")

class KannadaTranslationResponse(BaseModel):
    kannada_script: str = Field(description="Natural, polite spoken Kannada translation in Kannada script")
    pronunciation: str = Field(description="Easy-to-read English phonetic transliteration so any tourist can pronounce it accurately")
    meaning: str = Field(description="Accurate meaning in the user's chosen source language (English, Hindi, or Marathi)")
    cultural_tip: str = Field(description="Short helpful etiquette or cultural tip for using this phrase politely in Karnataka")

class ReverseTranslationResponse(BaseModel):
    detected_kannada: str = Field(description="Cleaned Kannada text or phonetic representation of what the local resident said")
    translation: str = Field(description="Accurate translation into the tourist's preferred language")
    context_explanation: str = Field(description="What the local person means in this context (e.g. why the auto driver said no change, or how to reply)")
    suggested_reply: str = Field(description="A polite short Kannada phrase the tourist can say in response, with phonetic pronunciation")

class HeritageStoryResponse(BaseModel):
    place_name: str = Field(description="Official name of the heritage monument or destination")
    location: str = Field(description="District and geographic location in Karnataka")
    founded_era: str = Field(description="Approximate century, year, or founding dynasty")
    overview: str = Field(description="Comprehensive introduction to what the place is and its present status")
    historical_significance: str = Field(description="Why this monument is nationally or globally important")
    story_behind_the_place: str = Field(description="Compelling historical narrative, founding legends, and events that occurred here")
    people_and_dynasties: str = Field(description="Kings, queens, patrons, and architects associated with this monument")
    historical_timeline: list[str] = Field(description="3-5 chronological bullet points of major historical milestones")
    architecture: str = Field(description="Construction style, carvings, stone used, and architectural uniqueness")
    cultural_importance: str = Field(description="Traditions, living temple rituals, and festivals associated with it")
    interesting_facts: list[str] = Field(description="3-4 verified, intriguing facts for curious tourists")
    what_to_observe: list[str] = Field(description="Specific carvings, acoustic features, or spots visitors must notice")
    verified_sources: list[str] = Field(description="Recognized heritage references e.g. Archaeological Survey of India (ASI), UNESCO, KSTDC")

class HeritageQAResponse(BaseModel):
    answer: str = Field(description="Detailed, respectful, and historically grounded answer to the traveller's question")
    key_takeaway: str = Field(description="One-sentence memorable takeaway")
    what_to_notice: str = Field(description="Physical detail the traveller can look for in person")


# ==========================================
# 5. SECURE API KEY RESOLUTION & ERROR SANITIZATION (GROQCLOUD)
# ==========================================
def get_groq_api_key() -> str:
    """
    Securely resolves the GroqCloud API key in priority order:
    1. Environment variable (loaded via python-dotenv from .env or system environment)
    2. Streamlit secrets (.streamlit/secrets.toml)
    3. UI Sidebar input (session state)
    Never prints, logs, or hardcodes credentials.
    """
    # 1. Environment variable (.env or system)
    env_key = os.getenv("GROQ_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    # 2. Streamlit secrets
    try:
        if "GROQ_API_KEY" in st.secrets and str(st.secrets["GROQ_API_KEY"]).strip():
            return str(st.secrets["GROQ_API_KEY"]).strip()
    except Exception:
        pass

    # 3. Sidebar UI input
    sidebar_key = st.session_state.get("user_groq_api_key", "").strip()
    if sidebar_key:
        return sidebar_key

    # Backward compatibility with legacy key if set
    legacy_key = os.getenv("GEMINI_API_KEY") or st.session_state.get("user_gemini_api_key", "").strip()
    if legacy_key and legacy_key.strip():
        return legacy_key.strip()

    return ""

# Backward compatibility alias
get_gemini_api_key = get_groq_api_key


def get_api_key_source() -> str:
    """Returns a friendly description of where the active key was detected, without exposing it."""
    if os.getenv("GROQ_API_KEY"):
        return ".env / System Environment (GROQ_API_KEY)"
    try:
        if "GROQ_API_KEY" in st.secrets and str(st.secrets["GROQ_API_KEY"]).strip():
            return "Streamlit Secrets (.streamlit/secrets.toml)"
    except Exception:
        pass
    if st.session_state.get("user_groq_api_key", "").strip():
        return "Interactive Sidebar Session"
    if os.getenv("GEMINI_API_KEY") and os.getenv("GEMINI_API_KEY", "").startswith("gsk_"):
        return ".env (GEMINI_API_KEY)"
    return "Not Configured"


def sanitize_error_message(err: Exception) -> str:
    """
    Sanitizes API error messages to provide clear, actionable feedback without
    ever exposing sensitive API keys or credentials.
    """
    msg = str(err)
    if "401" in msg or "invalid_api_key" in msg.lower() or "authentication" in msg.lower():
        return (
            "Authentication Error (401 Invalid Groq API Key): The provided Groq API Key is invalid or expired. "
            "Please check or generate a free key from GroqCloud Console (https://console.groq.com/keys)."
        )
    if "429" in msg or "rate_limit_exceeded" in msg.lower() or "quota" in msg.lower():
        return (
            "Free Rate Limit Exceeded (429 Quota): Groq free-tier rate limit reached (30 requests/min). "
            "GroqCloud automatically resets limits every minute. Please wait 10-15 seconds and try your request again."
        )
    if "404" in msg or "not_found" in msg.lower() or "model_not_found" in msg.lower():
        return (
            f"Model Unavailable (404 Not Found): The requested Groq model '{DEFAULT_GROQ_MODEL}' "
            "could not be reached. Please verify access at GroqCloud Console (https://console.groq.com)."
        )
    if "503" in msg or "unavailable" in msg.lower() or "overloaded" in msg.lower():
        return (
            "GroqCloud Service Temporarily Busy (503 Service Unavailable): Groq LPU is currently handling high volume. "
            "We automatically attempted retries; please wait a brief moment and try again."
        )

    # Sanitize any potential API key patterns (e.g. gsk_... or AIzaSy...)
    cleaned = re.sub(r'gsk_[A-Za-z0-9_-]+', '[PROTECTED_GROQ_KEY]', msg)
    cleaned = re.sub(r'AIzaSy[A-Za-z0-9_-]{33}', '[PROTECTED_API_KEY]', cleaned)
    return cleaned


def execute_groq_with_retry(client: Groq, model: str, messages: list[dict], response_format: dict = None, temperature: float = 0.7, max_retries: int = 3) -> str:
    """
    Executes a Groq API request with exponential backoff for transient 503/server errors.
    Fails fast for non-transient errors (401, 404, 429 quota).
    """
    last_exception = None
    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                response_format=response_format or {"type": "json_object"},
                temperature=temperature,
            )
            raw_text = completion.choices[0].message.content
            if not raw_text:
                raise RuntimeError("Groq returned an empty response.")
            return raw_text
        except Exception as e:
            last_exception = e
            msg = str(e).lower()
            # Transient server errors (503, unavailable, connection)
            if ("503" in msg or "unavailable" in msg or "connection" in msg) and attempt < max_retries - 1:
                sleep_seconds = 2 ** attempt  # 1s, 2s, 4s
                time.sleep(sleep_seconds)
                continue
            raise e
    raise last_exception

# Backward compatibility alias
execute_gemini_with_retry = execute_groq_with_retry


# ==========================================
# 6. GROQCLOUD AI GENERATION FUNCTIONS
# ==========================================
def generate_trip_itinerary(
    api_key: str,
    starting_city: str,
    trip_duration: int,
    total_budget: int,
    num_travellers: int,
    travel_interests: list[str],
    preferred_pace: str,
    destination: str = "All Karnataka / Flexible Circuit",
) -> dict:
    """
    Calls the GroqCloud API using the official Groq SDK to generate a
    completely custom Karnataka travel itinerary based on actual user selections.
    """
    if not api_key:
        raise ValueError(
            "Groq API key is missing. Please configure GROQ_API_KEY in your .env file or Streamlit secrets."
        )

    client = Groq(api_key=api_key)
    interests_str = ", ".join(travel_interests) if travel_interests else "General Karnataka exploration"
    cost_per_person = total_budget // max(num_travellers, 1)

    has_specific_dest = bool(destination and destination != "All Karnataka / Flexible Circuit")
    dest_focus_line = f"- Target Destination / Focus Hub: {destination}" if has_specific_dest else "- Target Destination: Flexible Karnataka Circuit"
    dest_rule = (
        f"1. DESTINATION FOCUS: The entire itinerary MUST be centered specifically on {destination} and its iconic sights, nature, and cultural highlights (e.g. if Coorg / Kodagu is selected, feature Madikeri Fort, Abbey Falls, Raja's Seat, coffee estate walks, Dubare Elephant Camp, Talakaveri, and Namdroling Monastery/Golden Temple in Bylakuppe). The journey should start or logically transit from {starting_city} to {destination}."
        if has_specific_dest
        else f"1. ROUTE PLANNING: The itinerary MUST start from or logically connect from {starting_city} through an optimal Karnataka travel circuit matching the chosen interests."
    )

    system_prompt = (
        "You are YatraSaathi AI, an expert travel planner for the state of Karnataka, India. "
        "You MUST generate a realistic, culturally rich itinerary matching the user's constraints. "
        "Output ONLY a valid JSON object matching this schema:\n"
        f"{json.dumps(ItineraryResponse.model_json_schema())}"
    )

    user_prompt = f"""
USER SELECTIONS:
{dest_focus_line}
- Starting City: {starting_city}
- Trip Duration: Exactly {trip_duration} day(s)
- Total Budget: ₹{total_budget:,} INR for {num_travellers} traveller(s) (~₹{cost_per_person:,} INR per person)
- Number of Travellers: {num_travellers}
- Travel Interests: {interests_str}
- Travel Pace: {preferred_pace}

STRICT REQUIREMENTS:
{dest_rule}
2. The itinerary MUST start from or logically connect from {starting_city} to the destination(s) in Karnataka.
3. You MUST generate an itinerary containing EXACTLY {trip_duration} day(s) in the 'days' list.
4. All places, temples, beaches, trails, and dining spots MUST be real locations within Karnataka, India.
5. The budget (~₹{cost_per_person:,} per person) and travel pace ({preferred_pace}) must realistically guide the activity choices.
6. Provide a realistic budget breakdown dividing total budget across transport, accommodation, food, and activities.
7. Highlight authentic regional dishes suited to the specific route (e.g., Mysore Pak/Mylari Dosa in Mysuru, Jolada Rotti in North Karnataka/Hampi, Akki Rotti and Kadambuttu in Coorg, Neer Dosa/Ghee Roast in Coastal Karnataka, Filter Coffee in Chikkamagaluru, Benne Dosa in Bengaluru).
8. Return strictly valid JSON object matching the requested schema.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response_text = execute_groq_with_retry(
        client=client,
        model=DEFAULT_GROQ_MODEL,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.7,
    )

    return json.loads(response_text)


def adapt_trip_itinerary(
    api_key: str,
    current_plan: dict,
    change_reason: str,
    custom_note: str,
) -> dict:
    """
    Calls the Groq API to adapt an existing itinerary in real time when plans change,
    producing an updated day-by-day plan while preserving original vacation flow.
    """
    if not api_key:
        raise ValueError("Groq API key is missing. Please provide your Groq API key in the sidebar or .env file.")

    client = Groq(api_key=api_key)
    plan_summary = current_plan.get("summary", "")
    plan_title = current_plan.get("title", "")
    days_json = json.dumps(current_plan.get("days", []))

    system_prompt = (
        "You are YatraSaathi AI's real-time adaptive re-routing engine for Karnataka tourism. "
        "The traveller's current vacation plan has encountered an unexpected disruption. Adapt the plan immediately. "
        "Output ONLY a valid JSON object matching this schema:\n"
        f"{json.dumps(RevisedItineraryResponse.model_json_schema())}"
    )

    user_prompt = f"""
CURRENT ITINERARY:
- Title: {plan_title}
- Summary: {plan_summary}
- Days: {days_json}

DISRUPTION ENCOUNTERED:
- Reason: {change_reason}
- Additional details from traveller: {custom_note if custom_note else 'None provided'}

REQUIREMENTS:
1. Identify which outdoor, high-effort, or delayed activities must be postponed or cancelled.
2. Substitute them with realistic, weather-safe, or time-adjusted alternatives in that same Karnataka destination area.
3. Provide a complete revised day-by-day itinerary in 'revised_days' reflecting the substituted schedule.
4. Provide a clear, comforting AI note explaining why this substitution preserves their vacation.
5. Return strictly valid JSON object matching the schema.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response_text = execute_groq_with_retry(
        client=client,
        model=DEFAULT_GROQ_MODEL,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.7,
    )

    return json.loads(response_text)


def translate_to_kannada(
    api_key: str,
    user_text: str,
    source_language: str = "English",
) -> dict:
    """Translates user text into natural, polite spoken Kannada with English phonetics and cultural tips."""
    if not api_key:
        raise ValueError("Groq API key is missing. Please provide your Groq API key in the sidebar or .env file.")

    client = Groq(api_key=api_key)
    system_prompt = (
        "You are Kannada Buddy AI, a warm, polite local Karnataka language guide. "
        "Translate tourist phrases into natural, respectful spoken Kannada. "
        "Output ONLY a valid JSON object matching this schema:\n"
        f"{json.dumps(KannadaTranslationResponse.model_json_schema())}"
    )

    user_prompt = f"""
INPUT PHRASE: "{user_text}"
SOURCE LANGUAGE: {source_language}

REQUIREMENTS:
1. Provide the Kannada translation in authentic Kannada script.
2. Provide an easy-to-read English phonetic transliteration so any visitor can pronounce it accurately.
3. Provide the exact meaning in {source_language}.
4. Provide a short, practical cultural or etiquette tip for speaking politely in Karnataka.
5. Return strictly valid JSON matching the schema.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response_text = execute_groq_with_retry(
        client=client,
        model=DEFAULT_GROQ_MODEL,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.6,
    )

    return json.loads(response_text)


def reverse_translate_kannada(
    api_key: str,
    kannada_input: str,
    target_language: str = "English",
) -> dict:
    """Translates Kannada heard from local residents back into the tourist's chosen language."""
    if not api_key:
        raise ValueError("Groq API key is missing. Please provide your Groq API key in the sidebar or .env file.")

    client = Groq(api_key=api_key)
    system_prompt = (
        "You are Kannada Buddy AI. A tourist heard a Kannada phrase from a local resident and needs to understand what was said. "
        "Output ONLY a valid JSON object matching this schema:\n"
        f"{json.dumps(ReverseTranslationResponse.model_json_schema())}"
    )

    user_prompt = f"""
KANNADA PHRASE HEARD: "{kannada_input}"
TOURIST'S LANGUAGE: {target_language}

REQUIREMENTS:
1. Clean up or identify the Kannada words spoken.
2. Provide an accurate translation in {target_language}.
3. Explain the local context (e.g. why the auto driver said this, or what is expected).
4. Provide a polite short Kannada reply with phonetic pronunciation that the tourist can say back.
5. Return strictly valid JSON matching the schema.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response_text = execute_groq_with_retry(
        client=client,
        model=DEFAULT_GROQ_MODEL,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.6,
    )

    return json.loads(response_text)


def get_heritage_story(
    api_key: str,
    monument_name: str,
    target_language: str = "English",
) -> dict:
    """Generates structured, verified historical storytelling for a Karnataka monument in the chosen language."""
    if not api_key:
        raise ValueError("Groq API key is missing. Please provide your Groq API key in the sidebar or .env file.")

    client = Groq(api_key=api_key)
    system_prompt = (
        "You are Heritage Storyteller AI, an official Karnataka tourism & history expert. "
        "Provide verified, engaging historical knowledge about this Karnataka heritage destination based on ASI & UNESCO records. "
        "Output ONLY a valid JSON object matching this schema:\n"
        f"{json.dumps(HeritageStoryResponse.model_json_schema())}"
    )

    user_prompt = f"""
MONUMENT / PLACE: {monument_name}
PRESENTATION LANGUAGE: {target_language}

STRICT HISTORICAL ACCURACY REQUIREMENTS:
1. Ground facts in reliable records from the Archaeological Survey of India (ASI), UNESCO, and established Karnataka history.
2. Do not invent dates, rulers, or citations. Clearly separate documented historical facts from folklore or legends.
3. Structure the output strictly across the requested schema fields.
4. Translate all explanations into {target_language} while keeping historical names and dates accurate.
5. Return strictly valid JSON matching the schema.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response_text = execute_groq_with_retry(
        client=client,
        model=DEFAULT_GROQ_MODEL,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.6,
    )

    return json.loads(response_text)


def ask_heritage_ai(
    api_key: str,
    monument_name: str,
    question: str,
    target_language: str = "English",
) -> dict:
    """Answers a specific historical or architectural question about a Karnataka heritage site."""
    if not api_key:
        raise ValueError("Groq API key is missing. Please provide your Groq API key in the sidebar or .env file.")

    client = Groq(api_key=api_key)
    system_prompt = (
        f"You are Heritage Storyteller AI. Answer traveller questions about {monument_name} in Karnataka accurately. "
        "Output ONLY a valid JSON object matching this schema:\n"
        f"{json.dumps(HeritageQAResponse.model_json_schema())}"
    )

    user_prompt = f"""
MONUMENT CONTEXT: {monument_name}
TRAVELLER'S QUESTION: "{question}"
RESPONSE LANGUAGE: {target_language}

REQUIREMENTS:
1. Provide a historically accurate, engaging answer based on archaeological and historical records.
2. Provide a single memorable key takeaway.
3. Point out a physical carving, structure, or detail the traveller should look for in person.
4. Return strictly valid JSON matching the schema.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response_text = execute_groq_with_retry(
        client=client,
        model=DEFAULT_GROQ_MODEL,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.6,
    )

    return json.loads(response_text)


def get_safe_budget_breakdown(plan_data: dict, total_budget: int, num_travellers: int) -> dict:
    """Safely extracts or calculates budget allocation components."""
    bb = plan_data.get("budget_breakdown")
    if isinstance(bb, dict) and "transport_estimate" in bb:
        t = bb.get("transport_estimate", 0)
        a = bb.get("accommodation_estimate", 0)
        f = bb.get("food_estimate", 0)
        act = bb.get("activities_estimate", 0)
        tot = t + a + f + act
        if tot > 0:
            return {
                "transport": t,
                "accommodation": a,
                "food": f,
                "activities": act,
                "total": tot,
                "remaining": max(0, total_budget - tot),
                "notes": bb.get("notes", "Estimates tailored to your selected itinerary and travel party."),
                "savings_tips": bb.get("savings_tips", [])
            }
    # Proportional calculation based on total_budget
    t = int(total_budget * 0.25)
    a = int(total_budget * 0.40)
    f = int(total_budget * 0.20)
    act = max(0, total_budget - (t + a + f))
    return {
        "transport": t,
        "accommodation": a,
        "food": f,
        "activities": act,
        "total": total_budget,
        "remaining": 0,
        "notes": "Standard Karnataka budget distribution across key travel components.",
        "savings_tips": [
            "Opt for KSRTC Airavat/Rajahamsa buses for comfortable intercity transit at half the price of private cabs.",
            "Choose certified KSTDC Mayura hotels near heritage sites for clean, budget-friendly stays.",
            "Enjoy meals at iconic local Darshinis and authentic Khanavalis for delicious regional meals under ₹120."
        ]
    }


# ==========================================
# 7. STATIC VERIFIED DATA
# ==========================================
DESTINATIONS = {
    "Mysuru": {
        "name": "Mysuru (ಮೈಸೂರು)",
        "tagline": "Palaces, Royal Heritage & Culture",
        "badge": "Royal Heritage",
        "image": "https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?auto=format&fit=crop&w=800&q=80",
        "description": "Palaces, royal heritage, and culture. Grand Dasara traditions, illuminated royal palaces, fragrant sandalwood, and silk weaving.",
        "highlights": [
            "Mysore Palace illumination & Durbar halls",
            "Chamundeshwari Temple & Chamundi Hill views",
            "Devaraja 130-year-old spice & flower bazaar"
        ],
        "best_time": "October to March",
        "delicacy": "Mylari Butter Dosa & Mysore Pak",
        "distance": "~145 km from Bengaluru (2h via Expressway / Vande Bharat)",
        "default_interests": ["🏛️ Heritage & Architecture", "🍛 Culinary Food Trail"]
    },
    "Hampi": {
        "name": "Hampi (ಹಂಪಿ)",
        "tagline": "Ancient Ruins & Vijayanagara History",
        "badge": "Ancient Ruins",
        "image": "https://images.unsplash.com/photo-1620766182966-c6eb5ed2b788?auto=format&fit=crop&w=800&q=80",
        "description": "Ancient ruins and Vijayanagara history. UNESCO granite boulder wonderland along the Tungabhadra river, active shrines, and stone chariots.",
        "highlights": [
            "Stone Chariot at Vijaya Vittala Complex",
            "Virupaksha Temple active 7th-century shrine",
            "Sunset coracle boat ride on Tungabhadra"
        ],
        "best_time": "November to February",
        "delicacy": "North Karnataka Jolada Rotti Oota",
        "distance": "~340 km from Bengaluru (6h via NH48 / Hampi Express)",
        "default_interests": ["🏛️ Heritage & Architecture", "🛕 Spiritual & Ancient Temples"]
    },
    "Coorg": {
        "name": "Coorg / Kodagu (ಕೊಡಗು)",
        "tagline": "Coffee Plantations, Misty Hills & Nature",
        "badge": "Misty Hills",
        "image": "https://images.unsplash.com/photo-1596402184320-417e7178b2cd?auto=format&fit=crop&w=800&q=80",
        "description": "Coffee plantations, misty hills, and nature. Emerald Western Ghats valleys, cascading waterfalls, and Kodava hospitality.",
        "highlights": [
            "Abbey Falls & Raja's Seat sunset viewpoint",
            "Guided coffee plantation walking trails",
            "Dubare Elephant Camp & Kaveri riverbank"
        ],
        "best_time": "September to March",
        "delicacy": "Kadambuttu (Rice Dumplings) & Akki Rotti",
        "distance": "~250 km from Bengaluru (5.5h via Kushalnagar)",
        "default_interests": ["☕ Coffee Estates & Hill Stations", "🌲 Nature & Western Ghats"]
    },
    "Gokarna": {
        "name": "Gokarna (ಗೋಕರ್ಣ)",
        "tagline": "Beaches, Coastal Scenery & Peaceful Escapes",
        "badge": "Coastal Escapes",
        "image": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=800&q=80",
        "description": "Beaches, coastal scenery, and peaceful escapes. Pristine Arabian Sea cliff walks, tranquil golden sand coves, and coastal serenity.",
        "highlights": [
            "Om Beach (naturally shaped like sacred ॐ)",
            "Kudle Beach cliffside sunset cafes",
            "Mahabaleshwar Temple Atmalinga coastal shrine"
        ],
        "best_time": "October to March",
        "delicacy": "Karavali Coastal Curry & Neer Dosa",
        "distance": "~480 km from Bengaluru (Overnight scenic train)",
        "default_interests": ["🏖️ Beaches & Coastal Life", "🛕 Spiritual & Ancient Temples"]
    },
    "Bengaluru": {
        "name": "Bengaluru (ಬೆಂಗಳೂರು)",
        "tagline": "Garden City & Tech Metropolis",
        "badge": "Modern Hub",
        "image": "https://images.unsplash.com/photo-1596176530529-78163a4f7af2?auto=format&fit=crop&w=800&q=80",
        "description": "India's dynamic tech capital blending 240-acre botanical gardens, historic palaces, craft breweries, and South Indian coffee culture.",
        "highlights": [
            "Lalbagh Botanical Garden glasshouse & lakes",
            "Bangalore Palace Tudor-style courtyards",
            "Vibrant VV Puram street food trail & microbreweries"
        ],
        "best_time": "Year-round (Pleasant highland climate)",
        "delicacy": "Crispy Benne Masala Dosa & Filter Coffee",
        "distance": "State Capital & Central Transit Gateway",
        "default_interests": ["🍛 Culinary Food Trail", "🏛️ Heritage & Architecture"]
    },
    "Gokarna": {
        "name": "Gokarna (ಗೋಕರ್ಣ)",
        "tagline": "Sacred Coastline & Pristine Beaches",
        "badge": "Coastal Serenity",
        "image": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=800&q=80",
        "description": "A tranquil blend of ancient sea-facing shrines and pristine Arabian Sea cliff treks, presenting a peaceful coastal sanctuary.",
        "highlights": [
            "Om Beach (naturally shaped like sacred ॐ)",
            "Kudle Beach cliffside sunset cafes",
            "Mahabaleshwar Temple Atmalinga coastal shrine"
        ],
        "best_time": "October to March",
        "delicacy": "Karavali Coastal Curry & Neer Dosa",
        "distance": "~480 km from Bengaluru (Overnight scenic train)",
        "default_interests": ["🏖️ Beaches & Coastal Life", "🛕 Spiritual & Ancient Temples"]
    },
    "Chikkamagaluru": {
        "name": "Chikkamagaluru (ಚಿಕ್ಕಮಗಳೂರು)",
        "tagline": "Coffee Highlands & Highest Peaks",
        "badge": "Peak Adventure",
        "image": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80",
        "description": "The birthplace of coffee in India, nestled at the foothills of Mullayanagiri, Karnataka's highest peak with rolling cloud valleys.",
        "highlights": [
            "Mullayanagiri peak sunrise trek (1,930 m)",
            "Baba Budangiri & Manikyadhara waterfall",
            "Heritage coffee estate stays & blossom trails"
        ],
        "best_time": "September to March",
        "delicacy": "Malanadu Pandi/Veg Sambar & Fresh Filter Coffee",
        "distance": "~245 km from Bengaluru (4.5h via Hassan)",
        "default_interests": ["🧗 Adventure & Trekking", "☕ Coffee Estates & Hill Stations"]
    }
}

DESTINATION_OPTIONS = [
    "All Karnataka / Flexible Circuit",
    "Coorg / Kodagu (ಕೊಡಗು)",
    "Mysuru (ಮೈಸೂರು)",
    "Hampi (ಹಂಪಿ)",
    "Gokarna (ಗೋಕರ್ಣ)",
    "Chikkamagaluru (ಚಿಕ್ಕಮಗಳೂರು)",
    "Bengaluru (ಬೆಂಗಳೂರು)",
]

# Curated Heritage Monuments
HERITAGE_MONUMENTS = {
    "Hampi": {
        "name": "Hampi (UNESCO World Heritage Site)",
        "district": "Vijayanagara District",
        "dynasty": "Vijayanagara Empire (14th - 16th Century)",
        "tagline": "The City of Victory Carved in Giant Boulders",
        "image": "https://images.unsplash.com/photo-1620766182966-c6eb5ed2b788?auto=format&fit=crop&w=800&q=80",
        "key_highlights": "Stone Chariot, 56 Musical Pillars at Vittala Temple, Virupaksha Temple",
        "source_url": "https://whc.unesco.org/en/list/241/",
        "source_label": "UNESCO World Heritage Centre",
    },
    "Mysore Palace": {
        "name": "Mysore Palace (Amba Vilas)",
        "district": "Mysuru District",
        "dynasty": "Wodeyar Dynasty (Designed by Henry Irwin, 1912)",
        "tagline": "One of India's Most Grand Royal Residences",
        "image": "https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?auto=format&fit=crop&w=800&q=80",
        "key_highlights": "Durbar Hall, Gombe Thotti, 100,000 Golden Incandescent Illumination",
        "source_url": "https://mysorepalace.karnataka.gov.in/",
        "source_label": "Karnataka Tourism / Mysore Palace Board",
    },
    "Halebidu & Belur": {
        "name": "Sacred Ensembles of the Hoysalas (UNESCO)",
        "district": "Hassan District",
        "dynasty": "Hoysala Empire (12th Century, King Vishnuvardhana)",
        "tagline": "Masterpieces of Stellate Soapstone Architecture",
        "image": "https://images.unsplash.com/photo-1596402184320-417e7178b2cd?auto=format&fit=crop&w=800&q=80",
        "key_highlights": "Hoysaleshwara Temple, Chennakeshava Madanika sculptures, Intricate filigree carvings",
        "source_url": "https://whc.unesco.org/en/list/1670/",
        "source_label": "UNESCO World Heritage Centre",
    },
    "Badami Cave Temples": {
        "name": "Badami Rock-Cut Cave Temples",
        "district": "Bagalkote District",
        "dynasty": "Early Chalukya Dynasty (6th Century CE)",
        "tagline": "Cradle of South Indian Rock-Cut Architecture",
        "image": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=800&q=80",
        "key_highlights": "18-armed dancing Nataraja, Agastya Lake views, Sandstone cliffs",
        "source_url": "https://asi.nic.in/",
        "source_label": "Archaeological Survey of India (ASI)",
    },
    "Pattadakal": {
        "name": "Pattadakal Monument Group (UNESCO)",
        "district": "Bagalkote District",
        "dynasty": "Chalukya Dynasty (7th - 8th Century CE)",
        "tagline": "Harmonious Synthesis of Northern & Southern Indian Architectural Styles",
        "image": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80",
        "key_highlights": "Virupaksha Temple, Rekha-Nagara & Dravidian shrines, Malaprabha riverbank",
        "source_url": "https://whc.unesco.org/en/list/239/",
        "source_label": "UNESCO World Heritage Centre",
    },
    "Gommateshwara (Shravanabelagola)": {
        "name": "Gommateshwara Monolith (Bahubali)",
        "district": "Hassan District",
        "dynasty": "Western Ganga Dynasty (981 CE, Chavundaraya)",
        "tagline": "The World's Tallest Free-Standing Monolithic Statue (57 ft)",
        "image": "https://images.unsplash.com/photo-1596176530529-78163a4f7af2?auto=format&fit=crop&w=800&q=80",
        "key_highlights": "Vindhyagiri Hill climb (650 steps), Mahamastakabhisheka ceremony, Serene expression",
        "source_url": "https://karnatakatourism.org/",
        "source_label": "Karnataka Tourism Official",
    }
}

# Offline Kannada Phrasebook Categories
KANNADA_OFFLINE_PHRASES = {
    "Auto & Taxi": [
        {
            "kannada": "ದಯವಿಟ್ಟು ಮೀಟರ್ ಹಾಕಿ ಹೋಗಿ",
            "phonetic": "Dayavittu meter haaki hogi",
            "meaning_en": "Please turn on the meter and go",
            "meaning_hi": "कृपया मीटर चालू करके चलिए",
            "meaning_mr": "कृपया मीटर सुरू करून चला",
            "tip": "Most autos in Bengaluru and Mysuru are legally required to run on meter during daytime."
        },
        {
            "kannada": "ಮೈಸೂರು ಅರಮನೆಗೆ ಎಷ್ಟು ಆಗುತ್ತೆ?",
            "phonetic": "Mysuru aramanege eshtu aagutte?",
            "meaning_en": "How much will it cost to Mysore Palace?",
            "meaning_hi": "मैसूर पैलेस तक कितना किराया होगा?",
            "meaning_mr": "म्हैसूर पॅलेसपर्यंत किती भाडे होईल?",
            "tip": "Always negotiate and agree on the fare before stepping into the vehicle."
        },
        {
            "kannada": "ಇಲ್ಲೇ ಹತ್ತಿರದಲ್ಲಿ ನಿಲ್ಲಿಸಿ",
            "phonetic": "Ille hatthiradalli nillisi",
            "meaning_en": "Please stop right here nearby",
            "meaning_hi": "यहीं पास में रोक दीजिए",
            "meaning_mr": "येथेच जवळ थांबवा",
            "tip": "Say this politely when you reach your landmark."
        },
        {
            "kannada": "ಚಿಲ್ಲರೆ ಇದೆಯಾ ನಿಮ್ಮ ಹತ್ತಿರ?",
            "phonetic": "Chillare ideya nimma hatthira?",
            "meaning_en": "Do you have loose change with you?",
            "meaning_hi": "क्या आपके पास छुट्टे पैसे हैं?",
            "meaning_mr": "तुमच्याकडे सुट्टे पैसे आहेत का?",
            "tip": "Carry ₹10, ₹20, and ₹50 notes as change is often scarce with drivers."
        }
    ],
    "Asking Directions": [
        {
            "kannada": "ಬಸ್ ನಿಲ್ದಾಣ ಎಲ್ಲಿದೆ?",
            "phonetic": "Bus nildaana ellide?",
            "meaning_en": "Where is the bus stand?",
            "meaning_hi": "बस स्टैंड कहाँ है?",
            "meaning_mr": "बस स्थानक कुठे आहे?",
            "tip": "Bus stations in Karnataka are called 'KSRTC' or 'BMTC' stands."
        },
        {
            "kannada": "ಈ ದಾರಿ ಹಂಪಿಗೆ ಹೋಗುತ್ತಾ?",
            "phonetic": "Ee daari Hampige hoguttaa?",
            "meaning_en": "Does this road go to Hampi?",
            "meaning_hi": "क्या यह रास्ता हम्पी जाता है?",
            "meaning_mr": "हा रस्ता हम्पीला जातो का?",
            "tip": "Locals will usually reply with 'Haudu' (Yes) or 'Illa' (No)."
        },
        {
            "kannada": "ಇಲ್ಲಿಂದ ಎಷ್ಟು ದೂರ ಇದೆ?",
            "phonetic": "Illinda eshtu doora ide?",
            "meaning_en": "How far is it from here?",
            "meaning_hi": "यहाँ से कितनी दूरी पर है?",
            "meaning_mr": "येथून किती अंतर आहे?",
            "tip": "Useful when trekking or walking to viewpoints in Coorg and Western Ghats."
        },
        {
            "kannada": "ನೇರವಾಗಿ ಹೋಗಿ ಎಡಕ್ಕೆ ತಿರುಗಿ",
            "phonetic": "Neravaagi hogi edakke thirugi",
            "meaning_en": "Go straight and turn left",
            "meaning_hi": "सीधे जाइए और बाईं ओर मुड़िए",
            "meaning_mr": "सरळ जा आणि डावीकडे वळा",
            "tip": "'Edakke' means left, 'Balakke' means right, 'Neravaagi' means straight."
        }
    ],
    "Hotels & Accommodation": [
        {
            "kannada": "ರೂಮಿನಲ್ಲಿ ಬಿಸಿ ನೀರು ಬರುತ್ತಾ?",
            "phonetic": "Roominalli bisi neeru baruttaa?",
            "meaning_en": "Is hot water available in the room?",
            "meaning_hi": "क्या कमरे में गरम पानी आता है?",
            "meaning_mr": "खोलीत गरम पाणी येते का?",
            "tip": "In cool hill stations like Coorg and Chikkamagaluru, hot water is essential in mornings."
        },
        {
            "kannada": "ಚೆಕ್-ಔಟ್ ಸಮಯ ಯಾವಾಗ?",
            "phonetic": "Check-out samaya yaavaaga?",
            "meaning_en": "What is the check-out time?",
            "meaning_hi": "चेक-आउट का समय क्या है?",
            "meaning_mr": "चेक-आउटची वेळ कोणती आहे?",
            "tip": "Most Karnataka heritage hotels have 11:00 AM or 12:00 PM check-out."
        },
        {
            "kannada": "ನನ್ನ ಲಗೇಜ್ ಇಲ್ಲಿ ಇಡಬಹುದಾ?",
            "phonetic": "Nanna luggage illi idabahudaa?",
            "meaning_en": "Can I leave my luggage here for some time?",
            "meaning_hi": "क्या मैं अपना सामान यहाँ कुछ देर रख सकता हूँ?",
            "meaning_mr": "मी माझे सामान येथे काही वेळ ठेवू शकतो का?",
            "tip": "Most hotels offer free luggage holding after check-out so you can sightsee."
        }
    ],
    "Restaurants & Food": [
        {
            "kannada": "ಇದು ತುಂಬಾ ಖಾರ ಇದೆಯಾ?",
            "phonetic": "Idu thumba khaara ideya?",
            "meaning_en": "Is this dish very spicy?",
            "meaning_hi": "क्या यह बहुत तीखा है?",
            "meaning_mr": "हे खूप तिखट आहे का?",
            "tip": "Karnataka coastal and North Karnataka cuisines can be fiery! Ask for 'Swalpa kammi khaara' for mild."
        },
        {
            "kannada": "ಒಂದು ಸ್ಪೆಷಲ್ ಫಿಲ್ಟರ್ ಕಾಫಿ ಕೊಡಿ",
            "phonetic": "Ondu special filter coffee kodi",
            "meaning_en": "Please give one special filter coffee",
            "meaning_hi": "एक स्पेशल फिल्टर कॉफ़ी दीजिए",
            "meaning_mr": "एक स्पेशल फिल्टर कॉफी द्या",
            "tip": "Karnataka is India's coffee heartland — filter coffee served in stainless steel dabara is a must!"
        },
        {
            "kannada": "ದಯವಿಟ್ಟು ಬಿಲ್ ತನ್ನಿ",
            "phonetic": "Dayavittu bill thanni",
            "meaning_en": "Please bring the bill",
            "meaning_hi": "कृपया बिल ले आइए",
            "meaning_mr": "कृपया बिल आणा",
            "tip": "A polite, standard closing phrase in any Darshini, hotel, or mess."
        },
        {
            "kannada": "ಇಲ್ಲಿ ಶುದ್ಧ ಸಸ್ಯಾಹಾರಿ ಊಟ ಸಿಗುತ್ತಾ?",
            "phonetic": "Illi shuddha sasyaahaari oota siguttaa?",
            "meaning_en": "Is pure vegetarian food available here?",
            "meaning_hi": "क्या यहाँ शुद्ध शाकाहारी भोजन मिलेगा?",
            "meaning_mr": "येथे शुद्ध शाकाहारी जेवण मिळेल का?",
            "tip": "Look for 'Shuddha Brahmaana / Shuddha Vaishnava' signboards for traditional satvik meals."
        }
    ],
    "Shopping & Payments": [
        {
            "kannada": "ಇದಕ್ಕೆ ಎಷ್ಟು ಬೆಲೆ?",
            "phonetic": "Idakke eshtu bele?",
            "meaning_en": "How much does this cost?",
            "meaning_hi": "इसकी कीमत कितनी है?",
            "meaning_mr": "याची किंमत किती आहे?",
            "tip": "Essential for shopping sandalwood crafts, spices, and silk sarees in Devaraja Market."
        },
        {
            "kannada": "ಸ್ವಲ್ಪ ಕಮ್ಮಿ ಮಾಡಿ ಕೊಡಿ",
            "phonetic": "Swalpa kammi maadi kodi",
            "meaning_en": "Can you please reduce the price a little?",
            "meaning_hi": "कृपया थोड़ा दाम कम कीजिए",
            "meaning_mr": "कृपया थोडी किंमत कमी करा",
            "tip": "Polite bargaining phrase for local handicraft street stalls."
        },
        {
            "kannada": "ಗೂಗಲ್ ಪೇ / ಫೋನ್ ಪೇ ಇದೆಯಾ?",
            "phonetic": "Google Pay / PhonePe ideya?",
            "meaning_en": "Do you accept Google Pay / PhonePe / UPI?",
            "meaning_hi": "क्या आप गूगल पे या फोनपे स्वीकार करते हैं?",
            "meaning_mr": "तुम्ही गुगल पे किंवा फोनपे घेता का?",
            "tip": "UPI is widely accepted across Karnataka, even at small coconut water stalls."
        }
    ],
    "Tourist Attractions": [
        {
            "kannada": "ಅರಮನೆ ಪ್ರವೇಶ ಸಮಯ ಯಾವಾಗ?",
            "phonetic": "Aramane pravesha samaya yaavaaga?",
            "meaning_en": "What time does the palace open for entry?",
            "meaning_hi": "महल में प्रवेश का समय क्या है?",
            "meaning_mr": "राजवाड्यात प्रवेशाची वेळ कोणती आहे?",
            "tip": "Mysore Palace is generally open 10:00 AM to 5:30 PM daily."
        },
        {
            "kannada": "ಎಂಟ್ರಿ ಟಿಕೆಟ್ ಎಲ್ಲಿ ಸಿಗುತ್ತದೆ?",
            "phonetic": "Entry ticket elli siguttade?",
            "meaning_en": "Where do I get the entry ticket?",
            "meaning_hi": "प्रवेश टिकट कहाँ मिलेगा?",
            "meaning_mr": "प्रवेश तिकीट कुठे मिळेल?",
            "tip": "Most ASI monuments (Hampi, Belur, Badami) now offer QR code digital ticket booking."
        },
        {
            "kannada": "ಇಲ್ಲಿ ಫೋಟೋ ತೆಗೆಯಲು ಅನುಮತಿ ಇದೆಯಾ?",
            "phonetic": "Illi photo tegeyalu anumathi ideya?",
            "meaning_en": "Is photography permitted here?",
            "meaning_hi": "क्या यहाँ फोटो खींचने की अनुमति है?",
            "meaning_mr": "येथे फोटो काढण्याची परवानगी आहे का?",
            "tip": "Inside sanctum sanctorums of ancient Karnataka temples, photography is strictly prohibited."
        }
    ],
    "General Conversation": [
        {
            "kannada": "ನಮಸ್ಕಾರ, ಹೇಗಿದ್ದೀರಾ?",
            "phonetic": "Namaskara, hegiddira?",
            "meaning_en": "Hello / Greetings, how are you?",
            "meaning_hi": "नमस्ते, आप कैसे हैं?",
            "meaning_mr": "नमस्कार, आपण कसे आहात?",
            "tip": "'Namaskara' with folded hands is the warmest, most respectful greeting in Karnataka."
        },
        {
            "kannada": "ತುಂಬಾ ಧನ್ಯವಾದಗಳು!",
            "phonetic": "Thumba dhanyavaadagalu!",
            "meaning_en": "Thank you very much!",
            "meaning_hi": "बहुत-बहुत धन्यवाद!",
            "meaning_mr": "खूप-खूप धन्यवाद!",
            "tip": "Using this phrase will instantly bring a warm smile to any local person's face."
        },
        {
            "kannada": "ನನಗೆ ಕನ್ನಡ ಸ್ವಲ್ಪ ಮಾತ್ರ ಬರುತ್ತೆ",
            "phonetic": "Nanage Kannada swalpa maathra barutte",
            "meaning_en": "I know only a little bit of Kannada",
            "meaning_hi": "मुझे थोड़ी ही कन्नड़ आती है",
            "meaning_mr": "मला थोडीच कन्नड येते",
            "tip": "Locals deeply appreciate tourists trying to speak even a few words of Kannada."
        },
        {
            "kannada": "ಕರ್ನಾಟಕ ತುಂಬಾ ಸುಂದರವಾಗಿದೆ!",
            "phonetic": "Karnataka thumba sundaravaagide!",
            "meaning_en": "Karnataka is exceedingly beautiful!",
            "meaning_hi": "कर्नाटक बहुत सुंदर है!",
            "meaning_mr": "कर्नाटक खूप सुंदर आहे!",
            "tip": "A lovely compliment to share with your homestay host or local taxi driver."
        }
    ],
    "Emergencies & Help": [
        {
            "kannada": "ದಯವಿಟ್ಟು ನನಗೆ ಸಹಾಯ ಮಾಡಿ",
            "phonetic": "Dayavittu nanage sahaaya maadi",
            "meaning_en": "Please help me",
            "meaning_hi": "कृपया मेरी मदद कीजिए",
            "meaning_mr": "कृपया मला मदत करा",
            "tip": "Universal emergency distress phrase understood everywhere across Karnataka."
        },
        {
            "kannada": "ಹತ್ತಿರದ ಆಸ್ಪತ್ರೆ ಎಲ್ಲಿದೆ?",
            "phonetic": "Hatthirada aaspatre ellide?",
            "meaning_en": "Where is the nearest hospital?",
            "meaning_hi": "पास का अस्पताल कहाँ है?",
            "meaning_mr": "जवळचे रुग्णालय कुठे आहे?",
            "tip": "Remember that Karnataka's universal emergency ambulance helpline is 108 or 112."
        },
        {
            "kannada": "ಪೊಲೀಸ್ ಸ್ಟೇಷನ್ ಎಲ್ಲಿದೆ?",
            "phonetic": "Police station ellide?",
            "meaning_en": "Where is the police station?",
            "meaning_hi": "पुलिस स्टेशन कहाँ है?",
            "meaning_mr": "पोलीस स्टेशन कुठे आहे?",
            "tip": "The integrated national police emergency number across Karnataka is 112."
        }
    ]
}


# ==========================================
# 8. TOP NAVIGATION BAR & PERSISTENT SESSION STATE
# ==========================================
# Pre-initialize core state variables
if "active_nav_section" not in st.session_state:
    st.session_state["active_nav_section"] = "🗺️ Plan My Trip"
if "form_destination" not in st.session_state:
    st.session_state["form_destination"] = "All Karnataka / Flexible Circuit"
if "form_starting_city" not in st.session_state:
    st.session_state["form_starting_city"] = "Bengaluru (ಬೆಂಗಳೂರು)"
if "form_duration" not in st.session_state:
    st.session_state["form_duration"] = 3
if "form_travellers" not in st.session_state:
    st.session_state["form_travellers"] = 2
if "form_budget" not in st.session_state:
    st.session_state["form_budget"] = 18000
if "form_interests" not in st.session_state:
    st.session_state["form_interests"] = ["🏛️ Heritage & Architecture", "🌲 Nature & Western Ghats"]
if "form_pace" not in st.session_state:
    st.session_state["form_pace"] = "Balanced (Best Sights)"
if "kannada_target_lang" not in st.session_state:
    st.session_state["kannada_target_lang"] = "English"

active_key = get_groq_api_key()
key_source_desc = get_api_key_source()

# Top Header Bar
st.markdown("""
<div class="top-navbar">
    <div class="brand-logo">
        <div class="brand-icon">🌿</div>
        <div>
            <div class="brand-title">YatraSaathi AI</div>
            <div class="brand-subtitle">Karnataka Smart Travel Planner • Version 4.0</div>
        </div>
    </div>
    <div style="display: flex; align-items: center; gap: 0.8rem; flex-wrap: wrap;">
        <span class="nav-badge">
            <span style="font-size: 0.9rem;">✨</span>
            Smart Karnataka Companion
        </span>
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 9. SIDEBAR CONFIGURATION & HELPLINES
# ==========================================
with st.sidebar:
    st.markdown("### 🌿 YatraSaathi AI")
    st.caption("Your personal AI travel companion for unforgettable Karnataka journeys.")
    
    st.divider()
    st.markdown("#### 🧭 Quick Navigation")
    nav_options = [
        "🏠 Home & Destinations",
        "🗺️ Plan My Trip",
        "⚡ My Plan Changed",
        "💰 Budget Optimizer",
        "🛡️ SafeRoute AI",
        "🗣️ Kannada Buddy AI",
        "🏛️ Heritage Storyteller AI",
    ]
    selected_nav = st.radio(
        "Jump to section:",
        options=nav_options,
        index=nav_options.index(st.session_state["active_nav_section"]) if st.session_state["active_nav_section"] in nav_options else 1,
        key="nav_radio_selector"
    )
    st.session_state["active_nav_section"] = selected_nav

    st.divider()
    st.markdown("#### 📞 Karnataka Traveler Helplines")
    st.markdown("🚨 **Universal Emergency:** `112`")
    st.markdown("🏛️ **Karnataka Tourism (KSTDC):** `080-43344334`")
    st.markdown("🚌 **KSRTC Bus Booking:** `080-26252625`")
    st.markdown("🚆 **Railway Enquiries:** `139`")
    st.markdown("🚑 **Ambulance:** `108`")


# ==========================================
# 10. SECTION A: HERO & DESTINATIONS SHOWCASE
# ==========================================
# Render Hero Section on Home & Overview
if st.session_state["active_nav_section"] in ["🏠 Home & Destinations", "🗺️ Plan My Trip"]:
    st.markdown("""
    <div class="hero-container">
        <div class="hero-pill">
            <span>✨</span> AI-Powered Karnataka Tourism • One State, Many Worlds
        </div>
        <div class="hero-heading">
            Discover Karnataka,<br>Your Way
        </div>
        <div class="hero-subheading">
            Your personal AI travel companion for unforgettable journeys. Explore royal palaces, 
            misty Western Ghats coffee estates, ancient UNESCO boulders, and sun-kissed coastal cliffs.
        </div>
        <div class="hero-features">
            <div class="feature-pill">🗺️ Personalised Itineraries</div>
            <div class="feature-pill">💳 Budget-Aware Planning</div>
            <div class="feature-pill">⚡ Adaptive Travel Support</div>
            <div class="feature-pill">🗣️ Kannada Buddy AI</div>
            <div class="feature-pill">🏛️ Heritage Storyteller AI</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# Destination selection callback
def on_select_destination(dest_key: str):
    dest_data = DESTINATIONS.get(dest_key)
    if dest_data:
        dest_name = dest_data["name"]
        st.session_state["form_destination"] = dest_name
        st.session_state["selected_dest_banner"] = dest_name
        st.session_state["active_nav_section"] = "🗺️ Plan My Trip"
        st.session_state["nav_radio_selector"] = "🗺️ Plan My Trip"
        st.session_state["scroll_to_planner"] = True
        # If user has no interests selected yet, populate recommended defaults
        if not st.session_state.get("form_interests"):
            st.session_state["form_interests"] = dest_data.get("default_interests", [])

def on_clear_destination():
    st.session_state["form_destination"] = "All Karnataka / Flexible Circuit"
    st.session_state.pop("selected_dest_banner", None)


# Companion feature navigation callbacks
def nav_to_adaptive():
    st.session_state["active_nav_section"] = "⚡ My Plan Changed"
    st.session_state["nav_radio_selector"] = "⚡ My Plan Changed"

def nav_to_budget():
    st.session_state["active_nav_section"] = "💰 Budget Optimizer"
    st.session_state["nav_radio_selector"] = "💰 Budget Optimizer"

def nav_to_kannada():
    st.session_state["active_nav_section"] = "🗣️ Kannada Buddy AI"
    st.session_state["nav_radio_selector"] = "🗣️ Kannada Buddy AI"


if st.session_state["active_nav_section"] in ["🏠 Home & Destinations", "🗺️ Plan My Trip"]:
    st.markdown("""
    <div class="section-title-wrap">
        <div class="section-eyebrow">Curated Flagship Experiences</div>
        <div class="section-title">✨ Discover Karnataka Differently</div>
        <div class="section-desc">Your next unforgettable Karnataka experience starts here.</div>
    </div>
    """, unsafe_allow_html=True)

    # Banner if destination was selected
    if st.session_state.get("selected_dest_banner"):
        st.success(
            f"🎯 **Destination Selected:** Target destination set to **{st.session_state['selected_dest_banner']}** in the trip planner below! "
            "[Jump to Plan Your Journey ↓](#plan-trip)"
        )

    # 4 Destination Cards in 4 columns
    featured_dest_keys = ["Mysuru", "Hampi", "Coorg", "Gokarna"]
    dest_cols = st.columns(4)
    for idx, key in enumerate(featured_dest_keys):
        dest = DESTINATIONS[key]
        with dest_cols[idx]:
            st.markdown(f"""
            <div class="dest-card-container">
                <div class="dest-image-wrap">
                    <img src="{dest['image']}" class="dest-image" alt="{dest['name']}">
                    <div class="dest-tag-badge">{dest['badge']}</div>
                </div>
                <div class="dest-content">
                    <div>
                        <div class="dest-name">{dest['name']}</div>
                        <div class="dest-tagline">{dest['tagline']}</div>
                        <div class="dest-desc">{dest['description']}</div>
                        <div class="dest-meta-grid">
                            <div class="dest-meta-item">📅 <strong>Best Time:</strong> {dest['best_time']}</div>
                            <div class="dest-meta-item">🍛 <strong>Must Eat:</strong> {dest['delicacy']}</div>
                            <div class="dest-meta-item">🚗 <strong>Distance:</strong> {dest['distance']}</div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.button(
                "Explore Destination",
                key=f"btn_plan_{key}",
                on_click=on_select_destination,
                args=(key,),
                use_container_width=True
            )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Smart Travel Companion Showcase
    st.markdown("""
    <div class="section-title-wrap">
        <div class="section-eyebrow">Smart Travel Technology</div>
        <div class="section-title">Your Smart Travel Companion</div>
        <div class="section-desc">AI-powered tools engineered specifically for exploring Karnataka with confidence, flexibility, and cultural ease.</div>
    </div>
    """, unsafe_allow_html=True)

    comp_col1, comp_col2, comp_col3 = st.columns(3)

    with comp_col1:
        st.markdown("""
        <div class="companion-card">
            <div>
                <div class="companion-icon">⚡</div>
                <div class="companion-title">Adaptive Travel Planner</div>
                <div class="companion-desc">
                    Update the itinerary when plans change. When rain hits Western Ghats trails or transit is delayed, 
                    our adaptive engine recalculates weather-safe alternatives while preserving your core schedule.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.button("⚡ Open Adaptive Planner", key="btn_nav_companion_adaptive", on_click=nav_to_adaptive, use_container_width=True)

    with comp_col2:
        st.markdown("""
        <div class="companion-card">
            <div>
                <div class="companion-icon">💰</div>
                <div class="companion-title">Smart Budget Insights</div>
                <div class="companion-desc">
                    Show estimated trip expenses and budget balance across transit, heritage stays, authentic meals, and permit fees 
                    with verified money-saving tips and remaining cushion tracking.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.button("💰 View Budget Insights", key="btn_nav_companion_budget", on_click=nav_to_budget, use_container_width=True)

    with comp_col3:
        st.markdown("""
        <div class="companion-card">
            <div>
                <div class="companion-icon">🗣️</div>
                <div class="companion-title">Kannada Travel Buddy</div>
                <div class="companion-desc">
                    Help travellers with useful Kannada phrases and pronunciation. Connect with auto drivers, shopkeepers, and locals effortlessly 
                    with instant offline phrases, audio pronunciation, and polite AI translation.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.button("🗣️ Open Kannada Buddy", key="btn_nav_companion_kannada", on_click=nav_to_kannada, use_container_width=True)

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)


# ==========================================
# 11. SECTION B: PLAN YOUR JOURNEY & AI ITINERARY
# ==========================================
if st.session_state["active_nav_section"] in ["🏠 Home & Destinations", "🗺️ Plan My Trip"]:
    st.markdown("<div id='plan-trip'></div>", unsafe_allow_html=True)

    # Smooth scroll if triggered
    if st.session_state.pop("scroll_to_planner", False):
        st.markdown("""
        <script>
            const plannerEl = document.getElementById('plan-trip');
            if (plannerEl) {
                plannerEl.scrollIntoView({behavior: 'smooth', block: 'start'});
            }
        </script>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="section-title-wrap">
        <div class="section-eyebrow">Interactive Trip Customizer</div>
        <div class="section-title">Plan Your Bespoke Journey</div>
        <div class="section-desc">Tailor every detail to your schedule, group size, budget, and travel interests.</div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        # Active destination focus indicator
        active_dest = st.session_state.get("form_destination", "All Karnataka / Flexible Circuit")
        if active_dest and active_dest != "All Karnataka / Flexible Circuit":
            b_col_text, b_col_btn = st.columns([4, 1.4])
            with b_col_text:
                st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.12); border-left: 5px solid #10B981; padding: 0.8rem 1.2rem; border-radius: 12px; border: 1px solid #28564C; border-left-width: 5px; margin-bottom: 0.8rem;">
                    <div style="font-weight: 700; color: #10B981; font-size: 1rem;">
                        🎯 Target Destination: {active_dest}
                    </div>
                    <div style="color: #D1D5DB; font-size: 0.86rem; margin-top: 2px;">
                        Your personalized itinerary will center on {active_dest} and neighboring attractions.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with b_col_btn:
                st.button("↺ Reset Destination", key="btn_reset_dest", on_click=on_clear_destination, use_container_width=True)
            st.markdown("<div style='height: 0.4rem;'></div>", unsafe_allow_html=True)
        
        col_a, col_b, col_c = st.columns([1.3, 1.2, 1.5])

        city_options = ["Bengaluru (ಬೆಂಗಳೂರು)", "Mysuru (ಮೈಸೂರು)", "Hubballi-Dharwad", "Mangaluru (ಮಂಗಳೂರು)", "Belagavi", "Shivamogga", "Other / Airport"]

        with col_a:
            destination = st.selectbox(
                "🎯 Target Destination / Focus Hub",
                options=DESTINATION_OPTIONS,
                key="form_destination",
                help="Choose your flagship destination or keep Flexible for AI circuit recommendations"
            )
            starting_city = st.selectbox(
                "📍 Starting City",
                options=city_options,
                key="form_starting_city",
                help="Where your Karnataka journey begins"
            )

        with col_b:
            trip_duration = st.slider(
                "⏱️ Trip Duration (Days)",
                min_value=1,
                max_value=14,
                key="form_duration",
                help="Total duration of your itinerary"
            )
            num_travellers = st.number_input(
                "👥 Number of Travellers",
                min_value=1,
                max_value=25,
                step=1,
                key="form_travellers",
                help="Number of people in your travel party"
            )

        with col_c:
            total_budget = st.slider(
                "💰 Total Budget (₹ INR)",
                min_value=3000,
                max_value=100000,
                step=1000,
                key="form_budget",
                help="Total estimated budget for the entire travel group"
            )
            preferred_pace = st.select_slider(
                "🚶 Travel Pace",
                options=["Relaxed & Leisurely", "Balanced (Best Sights)", "Action-Packed & Comprehensive"],
                key="form_pace"
            )

        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

        interest_options = [
            "🏛️ Heritage & Architecture",
            "🌲 Nature & Western Ghats",
            "🏖️ Beaches & Coastal Life",
            "🛕 Spiritual & Ancient Temples",
            "☕ Coffee Estates & Hill Stations",
            "🧗 Adventure & Trekking",
            "🍛 Culinary Food Trail"
        ]
        
        travel_interests = st.multiselect(
            "🎯 Travel Interests & Vibes",
            options=interest_options,
            key="form_interests",
            help="Choose what experiences matter most"
        )

        # Summary preview bar
        est_pp = total_budget // max(num_travellers, 1)
        st.markdown(f"""
        <div style="background: #0B302B; border-radius: 12px; padding: 0.85rem 1.3rem; margin-top: 1rem; border: 1px solid #28564C; display: flex; justify-content: space-between; align-items: center; font-size: 0.92rem; color: #F8F4E8;">
            <div><strong>Budget Allocation:</strong> ~₹{est_pp:,} INR per person for {trip_duration} days • <strong>Target Hub:</strong> {destination}</div>
            <div style="color: #10B981; font-weight: 700;">{preferred_pace}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

        btn_col1, btn_col2, btn_col3 = st.columns([1.2, 2, 1.2])
        with btn_col2:
            generate_btn = st.button("🚀 Generate My Itinerary", use_container_width=True, type="primary")

    current_user_inputs = {
        "destination": destination,
        "starting_city": starting_city,
        "trip_duration": trip_duration,
        "total_budget": total_budget,
        "num_travellers": num_travellers,
        "travel_interests": travel_interests,
        "preferred_pace": preferred_pace,
    }

    # Generation Execution Logic
    if generate_btn:
        api_key = get_groq_api_key()
        
        if not api_key:
            st.session_state["api_error"] = (
                "🔑 **GroqCloud API Key Missing:** YatraSaathi AI requires a GroqCloud API Key to generate dynamic, personalized itineraries. "
                "Please configure `GROQ_API_KEY=\"gsk_...\"` in your `.env` file or Streamlit Cloud secrets."
            )
            # DO NOT wipe existing valid itinerary on missing key!
        else:
            st.session_state.pop("api_error", None)
            with st.spinner("🤖 YatraSaathi AI is creating your personalized Karnataka itinerary via GroqCloud LPU..."):
                try:
                    plan = generate_trip_itinerary(
                        api_key=api_key,
                        starting_city=starting_city,
                        trip_duration=trip_duration,
                        total_budget=total_budget,
                        num_travellers=num_travellers,
                        travel_interests=travel_interests,
                        preferred_pace=preferred_pace,
                        destination=destination,
                    )
                    # Store safely in session state using consistent keys
                    st.session_state["generated_itinerary"] = plan
                    st.session_state["original_itinerary"] = plan
                    st.session_state["generated_plan"] = plan  # backward compatibility alias
                    st.session_state["generated_params"] = current_user_inputs
                    st.session_state.pop("revised_itinerary", None)
                    st.session_state.pop("adaptive_result", None)
                    st.session_state.pop("adaptive_error", None)
                except Exception as e:
                    st.session_state["api_error"] = f"❌ **Groq API Error:** {sanitize_error_message(e)}"
                    # Phase 2 Requirement: RETAIN the last successfully generated itinerary! Never delete it!

    if "api_error" in st.session_state:
        st.error(st.session_state["api_error"])
        if "GroqCloud API Key Missing" in st.session_state["api_error"] or "Groq API Key Missing" in st.session_state["api_error"]:
            with st.expander("🛠️ How to configure your Groq API Key", expanded=True):
                st.markdown("""
                1. **Local Development (.env):** Open `.env` in the project root and add:
                   ```env
                   GROQ_API_KEY="gsk_..."
                   ```
                2. **Streamlit Cloud Deployment:** Add `GROQ_API_KEY = "gsk_..."` in your App Settings > Secrets.
                3. **Get a free key:** Visit [GroqCloud Console (console.groq.com/keys)](https://console.groq.com/keys).
                """)

    # Display Generated Itinerary
    if "generated_itinerary" in st.session_state:
        plan_data = st.session_state["generated_itinerary"]
        saved_params = st.session_state.get("generated_params", {})
        
        if current_user_inputs != saved_params:
            st.warning("⚠️ **Notice:** You modified your travel preferences above. Click **'🚀 Generate My Itinerary'** to recalculate your plan with the new selections.")

        st.markdown("""
        <div class="section-title-wrap">
            <div class="section-eyebrow">Your Custom Plan</div>
            <div class="section-title">Your AI-Generated Itinerary</div>
            <div class="section-desc">Bespoke day-by-day plan crafted specifically for your group and schedule.</div>
        </div>
        """, unsafe_allow_html=True)

        st.success(f"✨ **{plan_data.get('title', 'Your Custom Karnataka Itinerary')}**")
        
        # Summary Metrics Row
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.metric("Total Duration", f"{len(plan_data.get('days', []))} Days")
        with kpi2:
            st.metric("Travellers", f"{saved_params.get('num_travellers', num_travellers)} Person(s)")
        with kpi3:
            st.metric("Est. Cost / Person", f"₹{plan_data.get('estimated_cost_per_person', total_budget // max(num_travellers, 1)):,}")
        with kpi4:
            st.metric("Primary Hub", plan_data.get("primary_hub", "Karnataka Circuit"))

        st.markdown(f"""
        <div style="background: #F5F3EB; border-radius: 14px; padding: 1.1rem 1.4rem; border: 1px solid #28564C; margin-bottom: 1.5rem; font-size: 0.98rem; line-height: 1.6; color: #102A2A;">
            <strong style="color: #102A2A;">Overview:</strong> {plan_data.get('summary', '')}
        </div>
        """, unsafe_allow_html=True)

        # Day-by-Day Timeline
        st.markdown("#### 📅 Day-by-Day Travel Timeline")
        days_list = plan_data.get("days", [])
        for idx, day_info in enumerate(days_list):
            st.markdown(f"""
            <div class="itinerary-day-card">
                <div class="day-badge-title">📌 {day_info.get('day', f'Day {idx+1}')}</div>
                <div class="time-slot">
                    <span class="time-icon">🌅</span>
                    <div><strong>Morning:</strong> {day_info.get('morning', '')}</div>
                </div>
                <div class="time-slot">
                    <span class="time-icon">☀️</span>
                    <div><strong>Afternoon:</strong> {day_info.get('afternoon', '')}</div>
                </div>
                <div class="time-slot">
                    <span class="time-icon">🌆</span>
                    <div><strong>Evening:</strong> {day_info.get('evening', '')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Regional Delicacies & Travel Insights
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("#### 🍛 Regional Karnataka Delicacies to Experience")
            dishes = plan_data.get("must_try_dishes", [])
            if dishes:
                for dish in dishes:
                    st.markdown(f"- 🍴 **{dish.get('name', '')}**: {dish.get('description', '')}")
            else:
                st.markdown("- 🥞 Mysore Masala Dosa & Benne Dosa\n- ☕ Authentic Coorg/Chikmagalur Filter Coffee\n- 🍚 Bisi Bele Bath & Akki Rotti")
        with col_t2:
            st.markdown("#### 💡 Practical Karnataka Travel Insights")
            tips = plan_data.get("travel_tips", [])
            if tips:
                for tip in tips:
                    st.markdown(f"- 📌 {tip}")
            else:
                st.markdown("- 🚆 Book Vande Bharat & KSRTC Airavat buses early.\n- 👚 Respect temple dress codes.\n- 🌦️ Pack monsoon essentials if visiting Western Ghats.")


# ==========================================
# 12. SECTION C: "MY PLAN CHANGED" (ADAPTIVE REPLANNING)
# ==========================================
if st.session_state["active_nav_section"] in ["🏠 Home & Destinations", "⚡ My Plan Changed"]:
    st.markdown("<div id='adaptive-replan'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-title-wrap">
        <div class="section-eyebrow">Real-Time Adaptability</div>
        <div class="section-title">My Plan Changed</div>
        <div class="section-desc">Vacations don't always go to plan. Tell YatraSaathi what disrupted your schedule, and let our adaptive engine recalculate without ruining your trip.</div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.8rem; flex-wrap: wrap;">
            <div style="font-family: 'Outfit', sans-serif; font-size: 1.35rem; font-weight: 700; color: #F8F4E8;">
                🧠 Adaptive AI Re-Routing Engine
            </div>
            <span class="nav-badge">⚡ Real-Time Recalculation</span>
        </div>
        <p style="color: #D1D5DB; font-size: 0.94rem; line-height: 1.5; margin-bottom: 1.2rem;">
            Whether unexpected monsoon rain hits the Western Ghats, a train is delayed by hours, or an attraction is closed, 
            YatraSaathi AI seamlessly substitutes blocked spots with weather-safe and time-adjusted alternatives while preserving your original plan.
        </p>
        """, unsafe_allow_html=True)

        replan_c1, replan_c2 = st.columns([1.5, 1])

        with replan_c1:
            change_reason = st.selectbox(
                "⚠️ What unexpected disruption occurred?",
                options=[
                    "🌧️ Heavy Rain / Monsoon Alert (Outdoor trails & viewpoints blocked)",
                    "⏰ Transport Delay (Train / Flight / Bus delayed by 3+ hours)",
                    "🔒 Attraction / Monument Closure (Unexpected weekly or VIP closure)",
                    "😴 Tired Travellers (Need relaxing, low-walking leisure schedule)",
                    "💰 Budget Constraint (Switching to free/low-cost heritage sights)"
                ],
                help="Select the real-world situation that disrupted your plan"
            )
            
            custom_note = st.text_input(
                "📝 Optional Note (e.g., 'Heavy rain near Abbey falls' or 'Travelling with elderly parents')",
                placeholder="Type any specific requirement or current location..."
            )

        with replan_c2:
            st.markdown("**How YatraSaathi Adapts:**")
            st.markdown("1. 🔍 **Detects Disruption:** Flags blocked outdoor or timed activities.")
            st.markdown("2. 🔄 **Substitutes:** Replaces with rain-safe or low-effort spots.")
            st.markdown("3. ⏱️ **Auto-Reschedules:** Preserves meal & departure timings.")
            
            adapt_button = st.button("⚡ Adapt My Itinerary", type="secondary", use_container_width=True)

        # Adaptive Replanning action
        if adapt_button:
            api_key = get_groq_api_key()
            if not api_key:
                st.session_state["adaptive_error"] = (
                    "🔑 **GroqCloud API Key Missing:** Please configure `GROQ_API_KEY` in your `.env` file or Streamlit Cloud secrets to use real-time adaptive replanning."
                )
                st.session_state.pop("revised_itinerary", None)
            elif "generated_itinerary" not in st.session_state:
                # Phase 2 Requirement: Show message ONLY if no valid itinerary is available!
                st.session_state["adaptive_error"] = (
                    "ℹ️ Please generate an itinerary first using **'🚀 Generate My Itinerary'** before adapting your schedule."
                )
                st.session_state.pop("revised_itinerary", None)
            else:
                st.session_state.pop("adaptive_error", None)
                with st.spinner("⚡ YatraSaathi AI is dynamically adapting your itinerary via GroqCloud LPU..."):
                    try:
                        replan_result = adapt_trip_itinerary(
                            api_key=api_key,
                            current_plan=st.session_state["generated_itinerary"],
                            change_reason=change_reason,
                            custom_note=custom_note,
                        )
                        # Phase 2 Requirement: Save revised itinerary separately to keep original intact!
                        st.session_state["revised_itinerary"] = replan_result
                        st.session_state["adaptive_result"] = replan_result  # backward compatibility alias
                    except Exception as e:
                        st.session_state["adaptive_error"] = f"❌ **Adaptive Replanning Error:** {sanitize_error_message(e)}"
                        # Retain existing plan on error!

        # Display adaptive replanning results or errors
        if "adaptive_error" in st.session_state:
            st.error(st.session_state["adaptive_error"])

        if "revised_itinerary" in st.session_state:
            replan = st.session_state["revised_itinerary"]
            st.markdown("---")
            
            # Action bar: Comparison & Restore button
            h_col1, h_col2 = st.columns([3, 1.2])
            with h_col1:
                st.markdown(f"### 🎯 Adapted Itinerary Solution: *{replan.get('situation_summary', change_reason)}*")
            with h_col2:
                def restore_original_itinerary():
                    st.session_state.pop("revised_itinerary", None)
                    st.session_state.pop("adaptive_result", None)
                st.button("↺ Restore Original Itinerary", key="btn_restore_orig", on_click=restore_original_itinerary, use_container_width=True)

            col_canc, col_adap = st.columns(2)
            with col_canc:
                canc_acts = "".join([f"<li style='margin-bottom: 5px;'>🛑 {act}</li>" for act in replan.get("postponed_activities", [])])
                st.markdown(f"""
                <div class="replan-col-cancelled">
                    <div style="font-weight: 700; color: #FCA5A5; font-size: 1.05rem; margin-bottom: 0.6rem;">
                        ❌ Postponed / Cancelled Activities
                    </div>
                    <ul style="padding-left: 1.2rem; margin: 0; color: #F8F4E8; font-size: 0.92rem;">
                        {canc_acts if canc_acts else "<li>None reported</li>"}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
            with col_adap:
                adap_acts = "".join([f"<li style='margin-bottom: 5px;'>✨ {alt}</li>" for alt in replan.get("adapted_alternatives", [])])
                st.markdown(f"""
                <div class="replan-col-adapted">
                    <div style="font-weight: 700; color: #6EE7B7; font-size: 1.05rem; margin-bottom: 0.6rem;">
                        ✅ Adapted Weather & Time-Safe Alternatives
                    </div>
                    <ul style="padding-left: 1.2rem; margin: 0; color: #F8F4E8; font-size: 0.92rem;">
                        {adap_acts if adap_acts else "<li>None reported</li>"}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                    
            if replan.get("ai_note"):
                st.markdown(f"""
                <div style="background: #0B302B; border-left: 4px solid #10B981; padding: 0.85rem 1.2rem; border-radius: 8px; margin-top: 1rem; font-size: 0.92rem; color: #F8F4E8; border: 1px solid #28564C; border-left-width: 4px;">
                    💡 <strong>AI Travel Rationale:</strong> {replan.get('ai_note')}
                </div>
                """, unsafe_allow_html=True)

            # Phase 2 Requirement: Display Side-by-Side or Tabbed view of Revised vs Original!
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            tab_revised, tab_original = st.tabs(["⚡ View Revised Schedule", "📜 Compare Original Schedule (Preserved)"])
            
            with tab_revised:
                revised_days = replan.get("revised_days", [])
                if revised_days:
                    for idx, d_info in enumerate(revised_days):
                        st.markdown(f"""
                        <div class="itinerary-day-card" style="border-left-color: #059669;">
                            <div class="day-badge-title">🔄 {d_info.get('day', f'Day {idx+1}')} <span style="font-size: 0.8rem; background: #ecfdf5; color: #065f46; padding: 3px 8px; border-radius: 12px; font-weight: 600;">Adapted</span></div>
                            <div class="time-slot"><span class="time-icon">🌅</span><div><strong>Morning:</strong> {d_info.get('morning', '')}</div></div>
                            <div class="time-slot"><span class="time-icon">☀️</span><div><strong>Afternoon:</strong> {d_info.get('afternoon', '')}</div></div>
                            <div class="time-slot"><span class="time-icon">🌆</span><div><strong>Evening:</strong> {d_info.get('evening', '')}</div></div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Your original plan was modified to incorporate the weather-safe alternatives listed above.")

            with tab_original:
                orig_plan = st.session_state.get("original_itinerary", {})
                orig_days = orig_plan.get("days", [])
                for idx, d_info in enumerate(orig_days):
                    st.markdown(f"""
                    <div class="itinerary-day-card" style="border-left-color: #64748b; opacity: 0.85;">
                        <div class="day-badge-title">📌 {d_info.get('day', f'Day {idx+1}')} <span style="font-size: 0.8rem; background: #f1f5f9; color: #475569; padding: 3px 8px; border-radius: 12px; font-weight: 600;">Original</span></div>
                        <div class="time-slot"><span class="time-icon">🌅</span><div><strong>Morning:</strong> {d_info.get('morning', '')}</div></div>
                        <div class="time-slot"><span class="time-icon">☀️</span><div><strong>Afternoon:</strong> {d_info.get('afternoon', '')}</div></div>
                        <div class="time-slot"><span class="time-icon">🌆</span><div><strong>Evening:</strong> {d_info.get('evening', '')}</div></div>
                    </div>
                    """, unsafe_allow_html=True)


# ==========================================
# 13. SECTION D: BUDGET OPTIMIZER
# ==========================================
if st.session_state["active_nav_section"] in ["🏠 Home & Destinations", "💰 Budget Optimizer"]:
    st.markdown("<div id='budget-optimizer'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-title-wrap">
        <div class="section-eyebrow">Financial Insights</div>
        <div class="section-title">Smart Budget Optimizer</div>
        <div class="section-desc">Algorithmically calculated cost breakdown across major vacation categories with money-saving recommendations.</div>
    </div>
    """, unsafe_allow_html=True)

    curr_budget = st.session_state.get("form_budget", 18000)
    curr_travellers = st.session_state.get("form_travellers", 2)
    active_plan = st.session_state.get("generated_itinerary", {})

    budget_info = get_safe_budget_breakdown(active_plan, curr_budget, curr_travellers)

    b_col1, b_col2, b_col3, b_col4 = st.columns(4)
    with b_col1:
        st.markdown(f"""
        <div class="budget-card">
            <div class="budget-label">🚗 Transport & Transit</div>
            <div class="budget-amount">₹{budget_info['transport']:,}</div>
            <div class="budget-share">Trains, cabs & local fuel</div>
        </div>
        """, unsafe_allow_html=True)
    with b_col2:
        st.markdown(f"""
        <div class="budget-card">
            <div class="budget-label">🏨 Lodging & Stay</div>
            <div class="budget-amount">₹{budget_info['accommodation']:,}</div>
            <div class="budget-share">Heritage hotels & homestays</div>
        </div>
        """, unsafe_allow_html=True)
    with b_col3:
        st.markdown(f"""
        <div class="budget-card">
            <div class="budget-label">🍛 Meals & Dining</div>
            <div class="budget-amount">₹{budget_info['food']:,}</div>
            <div class="budget-share">Traditional breakfasts & thalis</div>
        </div>
        """, unsafe_allow_html=True)
    with b_col4:
        st.markdown(f"""
        <div class="budget-card">
            <div class="budget-label">🎟️ Activities & Permits</div>
            <div class="budget-amount">₹{budget_info['activities']:,}</div>
            <div class="budget-share">Entry tickets, guides & safari</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: #0B302B; border-radius: 12px; padding: 0.9rem 1.4rem; margin-top: 1.2rem; border: 1px solid #28564C; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; font-size: 0.92rem; color: #F8F4E8;">
        <div><strong>Total Estimated Expenses:</strong> ₹{budget_info['total']:,} INR &nbsp;|&nbsp; <strong>Allocated Group Budget:</strong> ₹{curr_budget:,} INR</div>
        <div style="color: #10B981; font-weight: 700;">Remaining Cushion: ₹{budget_info['remaining']:,} INR</div>
    </div>
    <div style="font-size: 0.82rem; color: #D1D5DB; margin-top: 0.5rem; font-style: italic;">
        ℹ️ Note: Prices are algorithmically estimated indicative costs for planning purposes and may vary by season and booking preferences.
    </div>
    """, unsafe_allow_html=True)

    # Budget Saving Alternatives
    st.markdown("#### 💡 Value Optimization & Money-Saving Strategies")
    save_cols = st.columns(3)
    with save_cols[0]:
        st.markdown("""
        <div style="background: #F5F3EB; border: 1px solid #28564C; border-radius: 14px; padding: 1.2rem; height: 100%; color: #102A2A;">
            <strong style="color: #102A2A; font-size: 1rem;">🚌 Transit Optimization</strong><br>
            <span style="font-size: 0.88rem; color: #2D3748; line-height: 1.5; display: inline-block; margin-top: 0.35rem;">Book KSRTC Airavat Club Class or Vande Bharat Express between Bengaluru, Mysuru, and Hubballi to save up to 60% compared to private car rentals.</span>
        </div>
        """, unsafe_allow_html=True)
    with save_cols[1]:
        st.markdown("""
        <div style="background: #F5F3EB; border: 1px solid #28564C; border-radius: 14px; padding: 1.2rem; height: 100%; color: #102A2A;">
            <strong style="color: #102A2A; font-size: 1rem;">🏡 Government KSTDC Stays</strong><br>
            <span style="font-size: 0.88rem; color: #2D3748; line-height: 1.5; display: inline-block; margin-top: 0.35rem;">KSTDC Hotel Mayura properties are situated directly inside UNESCO heritage perimeters (Hampi, Belur) offering unbeatable prime locations at regulated rates.</span>
        </div>
        """, unsafe_allow_html=True)
    with save_cols[2]:
        st.markdown("""
        <div style="background: #F5F3EB; border: 1px solid #28564C; border-radius: 14px; padding: 1.2rem; height: 100%; color: #102A2A;">
            <strong style="color: #102A2A; font-size: 1rem;">🍛 Authentic Food Trails</strong><br>
            <span style="font-size: 0.88rem; color: #2D3748; line-height: 1.5; display: inline-block; margin-top: 0.35rem;">Dine at legendary local Darshinis and traditional Khanavalis for authentic Jolada Rotti, Benne Dosa, and Bisi Bele Bath at under ₹120 per meal.</span>
        </div>
        """, unsafe_allow_html=True)


# ==========================================
# 14. SECTION E: SAFEROUTE AI
# ==========================================
if st.session_state["active_nav_section"] in ["🏠 Home & Destinations", "🛡️ SafeRoute AI"]:
    st.markdown("<div id='saferoute-ai'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-title-wrap">
        <div class="section-eyebrow">Tourist Protection & Advisory</div>
        <div class="section-title">SafeRoute AI — Travel Safety & Weather Advisory</div>
        <div class="section-desc">Real-time precaution guidelines for weather disruptions, ghat roads, wildlife corridors, and emergency helplines.</div>
    </div>
    """, unsafe_allow_html=True)

    safe_c1, safe_c2 = st.columns(2)
    with safe_c1:
        st.markdown("""
        <div class="safety-alert-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
                <strong style="font-size:1.05rem; color:#0a1128;">🌦️ Western Ghats Monsoon & Fog Caution</strong>
                <span class="safety-warning-pill">Monsoon Caution</span>
            </div>
            <p style="font-size:0.9rem; color:#475569; line-height:1.5;">
                Charmadi Ghat, Shiradi Ghat, and Agumbe passes experience heavy mist and landslides between June and September. 
                Keep daytime travel schedules, maintain low fog lights, and avoid trekking unguided forest trails during red alerts.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="safety-alert-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
                <strong style="font-size:1.05rem; color:#0a1128;">🐘 Bandipur & Nagarahole Night Curfew</strong>
                <span class="safety-warning-pill">9 PM - 6 AM Curfew</span>
            </div>
            <p style="font-size:0.9rem; color:#475569; line-height:1.5;">
                NH-766 and NH-67 passing through Bandipur and Nagarahole National Parks are strictly closed to private vehicular traffic 
                from 9:00 PM to 6:00 AM to safeguard wildlife movement. Plan transit before dusk.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with safe_c2:
        st.markdown("""
        <div class="safety-alert-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
                <strong style="font-size:1.05rem; color:#0a1128;">🏖️ Arabian Sea Coastal Treks & High Tide</strong>
                <span class="safety-good-pill">Safety Guidelines</span>
            </div>
            <p style="font-size:0.9rem; color:#475569; line-height:1.5;">
                Gokarna cliff treks (between Kudle, Om, Half-Moon, and Paradise beaches) require sturdy footwear. 
                Never swim near rocky headlands or during high tide; follow red flag warnings erected by coastal lifesavers.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="safety-alert-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
                <strong style="font-size:1.05rem; color:#0a1128;">🏛️ UNESCO Monuments & Temple Etiquette</strong>
                <span class="safety-good-pill">Verified Protocol</span>
            </div>
            <p style="font-size:0.9rem; color:#475569; line-height:1.5;">
                Active temple shrines (Virupaksha in Hampi, Chamundeshwari in Mysuru) require modest shoulder-and-knee coverage. 
                Always hire government-licensed guides sporting official KSTDC identity badges.
            </p>
        </div>
        """, unsafe_allow_html=True)


# ==========================================
# 15. SECTION F: KANNADA BUDDY AI (SMART TRANSLATOR)
# ==========================================
if st.session_state["active_nav_section"] in ["🏠 Home & Destinations", "🗣️ Kannada Buddy AI"]:
    st.markdown("<div id='kannada-buddy'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-title-wrap">
        <div class="section-eyebrow">Local Language Assistant</div>
        <div class="section-title">Kannada Buddy AI — Your Karnataka Companion</div>
        <div class="section-desc">Connect with auto drivers, shopkeepers, and locals effortlessly. Speak respectful, natural Kannada with phonetic guides and audio pronunciation.</div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        # Language selection & Mode tabs
        col_lang, col_badge = st.columns([1, 1.2], vertical_alignment="bottom")
        with col_lang:
            target_lang = st.selectbox(
                "🌐 Choose your preferred language for explanations:",
                options=["English", "Hindi", "Marathi"],
                index=["English", "Hindi", "Marathi"].index(st.session_state.get("kannada_target_lang", "English")),
                key="kannada_lang_selector"
            )
            st.session_state["kannada_target_lang"] = target_lang

        with col_badge:
            st.markdown("""
            <div class="kannada-badge-row">
                <span class="offline-badge">⚡ Instant Offline Phrasebook</span>
                <span class="ai-badge">🤖 GroqCloud AI Translator</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 0.6rem;'></div>", unsafe_allow_html=True)

        kannada_tab1, kannada_tab2, kannada_tab3 = st.tabs([
            "📖 Instant Offline Phrasebook",
            "🤖 AI Custom Sentence Translator",
            "🔄 Reverse Translator (Understand Local Reply)"
        ])

        # TAB 1: OFFLINE PHRASEBOOK
        with kannada_tab1:
            st.markdown("##### 🧭 Essential Travel Phrases by Situation")
            st.caption("These essential travel phrases work instantly without internet access or API calls.")
            
            p_cat = st.selectbox("Select a travel situation:", list(KANNADA_OFFLINE_PHRASES.keys()), key="offline_cat_picker")
            phrases = KANNADA_OFFLINE_PHRASES[p_cat]

            for idx, p in enumerate(phrases):
                meaning_text = p.get(f"meaning_{target_lang[:2].lower()}", p["meaning_en"])
                st.markdown(f"""
                <div class="phrase-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                        <div>
                            <div class="phrase-kannada" style="font-size: 1.45rem; font-weight: 800; color: #0a1128; margin-bottom: 0.25rem;">
                                {p['kannada']}
                            </div>
                            <div class="phrase-phonetic" style="font-size: 1.05rem; font-weight: 600; color: #047857; font-style: italic; margin-bottom: 0.4rem;">
                                🗣️ "{p['phonetic']}"
                            </div>
                            <div class="phrase-meaning" style="font-size: 0.95rem; color: #334155; margin-bottom: 0.4rem;">
                                <strong>Meaning ({target_lang}):</strong> {meaning_text}
                            </div>
                            <div class="phrase-tip" style="font-size: 0.82rem; color: #64748b;">
                                💡 <em>{p['tip']}</em>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Interactive Audio and Copy buttons
                btn_cols = st.columns([1, 1, 2])
                with btn_cols[0]:
                    if st.button(f"🔊 Listen #{idx+1}", key=f"btn_audio_off_{p_cat}_{idx}"):
                        # Real browser Web Speech API implementation
                        components.html(f"""
                        <script>
                            if ('speechSynthesis' in window) {{
                                window.speechSynthesis.cancel();
                                const utter = new SpeechSynthesisUtterance("{p['kannada']}");
                                utter.lang = 'kn-IN';
                                utter.rate = 0.85;
                                window.speechSynthesis.speak(utter);
                            }} else {{
                                alert('Text-to-speech is not supported in this browser.');
                            }}
                        </script>
                        """, height=0)
                        st.toast(f"Playing Kannada: {p['phonetic']}")
                with btn_cols[1]:
                    if st.button(f"📋 Copy #{idx+1}", key=f"btn_copy_off_{p_cat}_{idx}"):
                        components.html(f"""
                        <script>
                            navigator.clipboard.writeText("{p['kannada']}");
                        </script>
                        """, height=0)
                        st.toast(f"Copied: {p['kannada']}")

        # TAB 2: AI CUSTOM TRANSLATOR
        with kannada_tab2:
            st.markdown("##### 💬 Type Anything to Speak Natural Kannada")
            st.caption("Powered by GroqCloud AI LPU — Translates complex or specific sentences into warm, spoken Kannada.")

            # Sample query callback helper
            def set_kannada_sample_query(sample_text: str):
                st.session_state["input_custom_kannada"] = sample_text

            user_query = st.text_input(
                f"Enter your sentence in {target_lang}:",
                placeholder="E.g., 'Please take me to Mysore Palace' or 'Can I pay via Google Pay?'",
                key="input_custom_kannada"
            )

            # Sample query buttons
            sample_col1, sample_col2, sample_col3 = st.columns(3)
            with sample_col1:
                st.button("👉 'Please take me to Mysore Palace'", on_click=set_kannada_sample_query, args=("Please take me to Mysore Palace",), use_container_width=True)
            with sample_col2:
                st.button("👉 'How much for 1kg of coffee powder?'", on_click=set_kannada_sample_query, args=("How much for 1kg of coffee powder?",), use_container_width=True)
            with sample_col3:
                st.button("👉 'Is there a vegetarian restaurant nearby?'", on_click=set_kannada_sample_query, args=("Is there a vegetarian restaurant nearby?",), use_container_width=True)

            if st.button("✨ Translate to Spoken Kannada", type="primary", use_container_width=True):
                user_text_val = user_query.strip() or st.session_state.get("input_custom_kannada", "").strip()
                if not user_text_val:
                    st.warning("Please type a sentence first.")
                else:
                    api_key = get_groq_api_key()
                    if not api_key:
                        st.error("🔑 Groq API key missing. Please provide your key in the sidebar or .env file.")
                    else:
                        with st.spinner("🤖 Translating into polite spoken Kannada via GroqCloud LPU..."):
                            try:
                                trans_res = translate_to_kannada(
                                    api_key=api_key,
                                    user_text=user_text_val,
                                    source_language=target_lang
                                )
                                st.session_state["last_kannada_trans"] = trans_res
                            except Exception as e:
                                st.error(f"❌ Translation Error: {sanitize_error_message(e)}")

            if "last_kannada_trans" in st.session_state:
                res = st.session_state["last_kannada_trans"]
                st.markdown(f"""
                <div class="kannada-output-card">
                    <div style="font-size: 0.8rem; text-transform: uppercase; color: #a7f3d0; font-weight: 700; letter-spacing: 1px; margin-bottom: 0.4rem;">
                        Kannada Script
                    </div>
                    <div class="kannada-script-text">
                        {res.get('kannada_script', '')}
                    </div>
                    <div class="kannada-phonetic-text">
                        🗣️ Pronounce as: "{res.get('pronunciation', '')}"
                    </div>
                    <div class="kannada-meaning-text">
                        <strong>Meaning in {target_lang}:</strong> {res.get('meaning', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if res.get("cultural_tip"):
                    st.markdown(f"""
                    <div class="kannada-tip-box">
                        💡 <strong>Polite Etiquette Tip:</strong> {res.get('cultural_tip')}
                    </div>
                    """, unsafe_allow_html=True)

                act_col1, act_col2 = st.columns(2)
                with act_col1:
                    if st.button("🔊 Listen Aloud", key="btn_audio_ai_trans", use_container_width=True):
                        components.html(f"""
                        <script>
                            if ('speechSynthesis' in window) {{
                                window.speechSynthesis.cancel();
                                const utter = new SpeechSynthesisUtterance("{res.get('kannada_script', '')}");
                                utter.lang = 'kn-IN';
                                utter.rate = 0.85;
                                window.speechSynthesis.speak(utter);
                            }}
                        </script>
                        """, height=0)
                        st.toast(f"Playing: {res.get('pronunciation', '')}")
                with act_col2:
                    if st.button("📋 Copy Kannada Script", key="btn_copy_ai_trans", use_container_width=True):
                        components.html(f"""
                        <script>
                            navigator.clipboard.writeText("{res.get('kannada_script', '')}");
                        </script>
                        """, height=0)
                        st.toast("Copied Kannada phrase to clipboard!")

        # TAB 3: REVERSE TRANSLATOR
        with kannada_tab3:
            st.markdown("##### 👂 Understand What the Local Person Said")
            st.caption("Enter what you heard (in Kannada script or phonetic English letters) to understand what they meant and how to politely reply.")

            def set_reverse_sample_query(sample_text: str):
                st.session_state["input_reverse_kannada"] = sample_text

            rev_input = st.text_input(
                "Enter what you heard (e.g., 'Chillare illa', 'Bega banni', 'Munde hogi'):",
                placeholder="E.g., 'Meter mele hattu roopaayi aagatte' or 'Bega banni'",
                key="input_reverse_kannada"
            )

            rev_sample1, rev_sample2, rev_sample3 = st.columns(3)
            with rev_sample1:
                st.button("👉 'Meter mele hattu roopaayi'", on_click=set_reverse_sample_query, args=("Meter mele hattu roopaayi",), use_container_width=True)
            with rev_sample2:
                st.button("👉 'Chillare illa'", on_click=set_reverse_sample_query, args=("Chillare illa",), use_container_width=True)
            with rev_sample3:
                st.button("👉 'Munde hogi'", on_click=set_reverse_sample_query, args=("Munde hogi",), use_container_width=True)

            if st.button("🔄 Translate Kannada Reply", use_container_width=True):
                rev_text_val = rev_input.strip() or st.session_state.get("input_reverse_kannada", "").strip()
                if not rev_text_val:
                    st.warning("Please enter what you heard.")
                else:
                    api_key = get_groq_api_key()
                    if not api_key:
                        st.error("🔑 Groq API key missing. Please provide your key in the sidebar or .env file.")
                    else:
                        with st.spinner("🤖 Deciphering local Kannada response via GroqCloud LPU..."):
                            try:
                                rev_res = reverse_translate_kannada(
                                    api_key=api_key,
                                    kannada_input=rev_text_val,
                                    target_language=target_lang
                                )
                                st.session_state["last_reverse_trans"] = rev_res
                            except Exception as e:
                                st.error(f"❌ Reverse Translation Error: {sanitize_error_message(e)}")

            if "last_reverse_trans" in st.session_state:
                r_res = st.session_state["last_reverse_trans"]
                st.markdown(f"""
                <div class="kannada-reverse-card">
                    <div style="color:#047857; font-weight:700; font-size:1.1rem; margin-bottom:0.4rem;">
                        Detected: "{r_res.get('detected_kannada', '')}"
                    </div>
                    <div class="reverse-trans-text" style="font-size:1.05rem; color:#0a1128; margin-bottom:0.6rem;">
                        <strong>Translation in {target_lang}:</strong> {r_res.get('translation', '')}
                    </div>
                    <div class="reverse-context-box" style="font-size:0.9rem; color:#475569; margin-bottom:0.8rem; background:#f8fafc; padding:0.75rem; border-radius:8px;">
                        💡 <strong>Context Explanation:</strong> {r_res.get('context_explanation', '')}
                    </div>
                    <div class="reverse-reply-box" style="background:#ecfdf5; border-left:4px solid #047857; padding:0.8rem 1.1rem; border-radius:8px; color:#065f46; font-size:0.95rem;">
                        🗣️ <strong>Suggested Polite Reply:</strong> {r_res.get('suggested_reply', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ==========================================
# 16. SECTION G: HERITAGE STORYTELLER AI
# ==========================================
if st.session_state["active_nav_section"] in ["🏠 Home & Destinations", "🏛️ Heritage Storyteller AI"]:
    st.markdown("<div id='heritage-storyteller'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-title-wrap">
        <div class="section-eyebrow">Living History & Cultural Lore</div>
        <div class="section-title">Heritage Storyteller AI — Discover the Stories of Karnataka</div>
        <div class="section-desc">Unlock centuries of architectural wonders, royal dynasties, and temple carvings with verified historical knowledge and an interactive AI guide.</div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        # Language Selector for Stories
        col_hlang, col_hinfo = st.columns([1.5, 2])
        with col_hlang:
            story_lang = st.selectbox(
                "🌐 Read historical explanations in:",
                options=["English", "Hindi", "Marathi", "Kannada"],
                key="heritage_story_lang"
            )

        with col_hinfo:
            st.markdown("""
            <div style="text-align:right; font-size:0.85rem; color:#475569; margin-top:1.5rem;">
                🏛️ Sources: Archaeological Survey of India (ASI) • UNESCO • Karnataka Tourism
            </div>
            """, unsafe_allow_html=True)

        # Flagship Monument Quick-Cards
        st.markdown("##### 🏛️ Choose a Flagship Heritage Destination to Explore:")
        m_keys = list(HERITAGE_MONUMENTS.keys())
        m_cols = st.columns(3)
        for i, m_key in enumerate(m_keys):
            m_data = HERITAGE_MONUMENTS[m_key]
            with m_cols[i % 3]:
                st.markdown(f"""
                <div class="heritage-monument-card">
                    <img src="{m_data['image']}" style="width:100%; height:160px; object-fit:cover;" alt="{m_data['name']}">
                    <div style="padding:1.1rem;">
                        <div style="font-weight:700; font-size:1.1rem; color:#0a1128; margin-bottom:0.2rem;">{m_data['name']}</div>
                        <div style="font-size:0.8rem; color:#047857; font-weight:600; margin-bottom:0.5rem;">{m_data['dynasty']}</div>
                        <div style="font-size:0.85rem; color:#475569; margin-bottom:0.8rem;">{m_data['tagline']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Dual action buttons: Explore Stories & Add to Trip
                act_c1, act_c2 = st.columns(2)
                with act_c1:
                    if st.button(f"📖 Explore", key=f"btn_explore_mon_{i}", use_container_width=True):
                        st.session_state["selected_heritage_monument"] = m_key
                        st.session_state["active_nav_section"] = "🏛️ Heritage Storyteller AI"
                with act_c2:
                    if st.button(f"🎯 Add to Trip", key=f"btn_add_mon_{i}", use_container_width=True):
                        # Phase 5 Requirement: Connect to existing trip-planning workflow
                        matched_dest = "Hampi" if "Hampi" in m_key else ("Mysuru" if "Mysore" in m_key else "All Karnataka / Flexible Circuit")
                        if matched_dest in DESTINATIONS:
                            on_select_destination(matched_dest)
                        else:
                            st.session_state["form_destination"] = m_data["name"]
                            st.session_state["active_nav_section"] = "🗺️ Plan My Trip"
                        st.toast(f"Added {m_key} to your Trip Planner!")

        # Free search bar for any monument
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        search_query = st.text_input(
            "🔍 Or search any historical fort, temple, palace, or ruins in Karnataka:",
            placeholder="E.g., 'Bidar Fort', 'Chitradurga Fort', 'Gol Gumbaz', 'Somnathapura Temple'...",
            key="input_heritage_search"
        )
        if search_query:
            if st.button(f"🔎 Tell Me the Story of {search_query}", type="primary"):
                st.session_state["selected_heritage_monument"] = search_query

        # Display Detailed Heritage Story & Q&A
        active_monument = st.session_state.get("selected_heritage_monument", "Hampi")
        if active_monument:
            st.markdown("---")
            st.markdown(f"### 📜 Historical Chronicler: *{active_monument}*")

            # Check if story already cached in session state for this monument & language
            cache_key = f"story_{active_monument}_{story_lang}"
            if cache_key not in st.session_state:
                api_key = get_groq_api_key()
                if not api_key:
                    st.warning("🔑 Groq API key missing. Enter your key in the sidebar or .env to unlock real-time AI historical storytelling.")
                    story_data = None
                else:
                    with st.spinner(f"🏛️ Retrieving verified historical archives for {active_monument} in {story_lang} via GroqCloud LPU..."):
                        try:
                            story_data = get_heritage_story(api_key, active_monument, story_lang)
                            st.session_state[cache_key] = story_data
                        except Exception as e:
                            st.error(f"❌ Error generating heritage story: {sanitize_error_message(e)}")
                            story_data = None
            else:
                story_data = st.session_state[cache_key]

            if story_data:
                # Banner Overview
                st.markdown(f"""
                <div class="heritage-hero-banner">
                    <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; color: #a7f3d0; margin-bottom: 0.3rem;">
                        📍 {story_data.get('location', 'Karnataka')} • Era: {story_data.get('founded_era', 'Ancient')}
                    </div>
                    <div style="font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 800; margin-bottom: 0.8rem;">
                        {story_data.get('place_name', active_monument)}
                    </div>
                    <div style="font-size: 1.05rem; line-height: 1.6; color: #e2e8f0; max-width: 900px;">
                        {story_data.get('overview', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 9 Structured Historical Sections (Phase 5 Requirement)
                h_col_left, h_col_right = st.columns(2)
                
                with h_col_left:
                    st.markdown(f"""
                    <div class="heritage-section-box">
                        <h4 style="color:#102A2A; margin-top:0; font-family:'Outfit',sans-serif; font-weight:700;">👑 Historical Significance & Rulers</h4>
                        <p style="color:#102A2A; margin-bottom:0.4rem; font-size:0.92rem; line-height:1.5;"><strong>Why it Matters:</strong> {story_data.get('historical_significance', '')}</p>
                        <p style="color:#102A2A; margin-bottom:0; font-size:0.92rem; line-height:1.5;"><strong>Dynasties & Figures:</strong> {story_data.get('people_and_dynasties', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="heritage-section-box">
                        <h4 style="color:#102A2A; margin-top:0; font-family:'Outfit',sans-serif; font-weight:700;">📖 The Story Behind the Monument</h4>
                        <div style="color:#102A2A; line-height:1.6; font-size:0.92rem;">{story_data.get('story_behind_the_place', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    timeline_items = "".join([f"<li style='margin-bottom:4px;'>📌 {item}</li>" for item in story_data.get("historical_timeline", [])])
                    st.markdown(f"""
                    <div class="heritage-section-box">
                        <h4 style="color:#102A2A; margin-top:0; font-family:'Outfit',sans-serif; font-weight:700;">⏳ Chronological Historical Timeline</h4>
                        <ul style="padding-left:1.2rem; margin:0; color:#102A2A; font-size:0.92rem; line-height:1.5;">
                            {timeline_items}
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

                with h_col_right:
                    st.markdown(f"""
                    <div class="heritage-section-box">
                        <h4 style="color:#102A2A; margin-top:0; font-family:'Outfit',sans-serif; font-weight:700;">🏛️ Architecture & Carvings</h4>
                        <div style="color:#102A2A; line-height:1.6; font-size:0.92rem;">{story_data.get('architecture', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="heritage-section-box">
                        <h4 style="color:#102A2A; margin-top:0; font-family:'Outfit',sans-serif; font-weight:700;">🌺 Cultural Importance & Traditions</h4>
                        <div style="color:#102A2A; line-height:1.6; font-size:0.92rem;">{story_data.get('cultural_importance', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    observe_items = "".join([f"<li style='margin-bottom:4px;'>🔍 {obs}</li>" for obs in story_data.get("what_to_observe", [])])
                    st.markdown(f"""
                    <div class="heritage-section-box">
                        <h4 style="color:#102A2A; margin-top:0; font-family:'Outfit',sans-serif; font-weight:700;">👀 What to Observe on Your Visit</h4>
                        <ul style="padding-left:1.2rem; margin:0; color:#102A2A; font-size:0.92rem; line-height:1.5;">
                            {observe_items}
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

                # Interesting facts & Verified Sources
                st.markdown("#### ✨ Intriguing Facts & Documented References")
                f_cols = st.columns(2)
                with f_cols[0]:
                    for f in story_data.get("interesting_facts", []):
                        st.markdown(f"- 💡 {f}")
                with f_cols[1]:
                    st.markdown("**Verified Historical Sources:**")
                    sources = story_data.get("verified_sources", ["Archaeological Survey of India (ASI)", "UNESCO World Heritage Centre", "Karnataka State Tourism Development Corporation (KSTDC)"])
                    for s in sources:
                        st.markdown(f"- 🏛️ {s}")

            # INTERACTIVE "ASK AI ABOUT THIS PLACE" Q&A (Phase 5 Requirement)
            st.markdown("---")
            st.markdown(f"#### ❓ Ask AI About *{active_monument}*")
            st.caption(f"Curious about a carving, local legend, or king? Ask anything about {active_monument} in {story_lang}.")

            q_sample1, q_sample2, q_sample3 = st.columns(3)
            user_mon_q = st.text_input(
                f"Your question about {active_monument}:",
                placeholder="E.g., 'What do the carvings represent?' or 'Who built the stone chariot?'",
                key="input_heritage_qa"
            )

            with q_sample1:
                if st.button("👉 'Why is this place important?'", use_container_width=True):
                    user_mon_q = "Why is this place historically important?"
            with q_sample2:
                if st.button("👉 'Who built it and when?'", use_container_width=True):
                    user_mon_q = "Who built this monument and when?"
            with q_sample3:
                if st.button("👉 'Are there any local legends?'", use_container_width=True):
                    user_mon_q = "Are there any famous local legends or folklore associated with this place?"

            if st.button(f"💬 Ask Storyteller AI", type="secondary", use_container_width=True):
                if not user_mon_q.strip():
                    st.warning("Please type a question first.")
                else:
                    api_key = get_groq_api_key()
                    if not api_key:
                        st.error("🔑 Groq API key missing. Please provide your key in the sidebar or .env file.")
                    else:
                        with st.spinner(f"🤖 Consulting historical archives for {active_monument} via GroqCloud LPU..."):
                            try:
                                qa_res = ask_heritage_ai(api_key, active_monument, user_mon_q, story_lang)
                                st.session_state["last_heritage_qa"] = qa_res
                            except Exception as e:
                                st.error(f"❌ Q&A Error: {sanitize_error_message(e)}")

            if "last_heritage_qa" in st.session_state:
                q_res = st.session_state["last_heritage_qa"]
                st.markdown(f"""
                <div style="background: #F5F3EB; border: 1px solid #28564C; border-left: 5px solid #10B981; border-radius: 14px; padding: 1.4rem; margin-top: 1rem; color: #102A2A;">
                    <div style="font-weight: 700; color: #10B981; font-size: 1.15rem; margin-bottom: 0.6rem;">
                        💡 {q_res.get('key_takeaway', '')}
                    </div>
                    <div style="font-size: 1rem; color: #102A2A; line-height: 1.6; margin-bottom: 0.8rem;">
                        {q_res.get('answer', '')}
                    </div>
                    <div style="font-size: 0.88rem; color: #102A2A; background: #EAE6DB; padding: 0.75rem 1rem; border-radius: 8px; border: 1px solid #28564C;">
                        🔍 <strong>What to notice in person:</strong> {q_res.get('what_to_notice', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ==========================================
# 17. FOOTER
# ==========================================
st.markdown("""
<div class="footer-container">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; margin-bottom: 1.2rem;">
        <div>
            <div class="footer-brand">🌿 YatraSaathi AI</div>
            <div class="footer-tagline">Explore More. Worry Less. One State, Many Worlds.</div>
        </div>
        <div style="font-size: 0.85rem; color: #a7f3d0; font-weight: 600;">
            Karnataka Tourism • ಒಂದು ರಾಜ್ಯ, ಹಲವು ಜಗತ್ತು
        </div>
    </div>
    <div class="footer-links">
        Emergency: <strong>112</strong> &nbsp;|&nbsp; KSTDC: <strong>080-43344334</strong> &nbsp;|&nbsp; KSRTC: <strong>080-26252625</strong> &nbsp;|&nbsp; Railways: <strong>139</strong><br>
        Engineered with 💚 using Python, Streamlit &amp; GroqCloud LPU — YatraSaathi AI v4.0.
    </div>
</div>
""", unsafe_allow_html=True)
