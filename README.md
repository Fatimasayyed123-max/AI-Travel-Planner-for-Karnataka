# 🌿 YatraSaathi AI (ಯಾತ್ರಾಸಾಥಿ)
### An Adaptive AI Travel Planner for Karnataka | National Hackathon Edition

> **"One State, Many Worlds — ಒಂದು ರಾಜ್ಯ, ಹಲವು ಜಗತ್ತು"**  
> **"Explore More. Worry Less."**  
> YatraSaathi AI is an intelligent travel planner crafted to showcase the heritage, coastal beauty, and lush Western Ghats of Karnataka, powered by **Google Gemini AI** and featuring **real-time adaptive re-planning** when disruptions occur.

---

## 🌟 What's New in Version 3.0 (Premium Redesign)

1. **Travel-Tech Startup Aesthetic**:
   - Palette: **Emerald Green** (`#047857`, `#10b981`), **Deep Navy** (`#0a1128`, `#0f172a`), **Warm Cream** (`#fdfbf7`), and **Crisp White** (`#ffffff`).
   - Clean floating glassmorphism navbar and typography powered by *Plus Jakarta Sans* and *Outfit*.
2. **Hero Section ("Discover Karnataka, Your Way")**:
   - Backdrop image showcasing Karnataka's signature heritage and Western Ghats waterfalls with a dark emerald-navy gradient overlay.
   - Highlights: *Personalised Itineraries*, *Budget-Aware Planning*, *Adaptive Travel Support*, and *Authentic Culinary Trails*.
3. **6 Curated Flagship Destination Cards**:
   - **Mysuru**: Heritage Capital • Mysore Palace, Chamundi Hills, silk weaving & Mysore Pak.
   - **Coorg (Kodagu)**: Scotland of India • Misty coffee estates, Abbey Falls, Raja's Seat & Akki Rotti.
   - **Hampi**: Ancient UNESCO Wonder • Stone Chariot, 14th-century ruins & Tungabhadra coracle rides.
   - **Bengaluru**: Garden City & Tech Metropolis • Lalbagh, Bangalore Palace & craft coffee culture.
   - **Gokarna**: Sacred Coastline • Om Beach, Kudle cliffs & Mahabaleshwar Temple.
   - **Chikkamagaluru**: Coffee Highlands • Mullayanagiri peak (1,930 m) & coffee blossom aroma.
   - **Interactive Selection**: Clicking **"Plan Trip to [Destination]"** fast-tracks and pre-fills your trip planner form!
4. **Interactive Trip Customizer ("Plan Your Journey")**:
   - Modern executive form with Starting City, Duration slider, Budget slider with live per-person display, Traveller count, Interests multiselect, and Travel Pace.
   - Prominent **"🚀 Generate My Itinerary"** button with dynamic Gemini AI generation.
5. **AI-Generated Itinerary with Day-by-Day Timeline**:
   - Day-by-day timeline cards separating **🌅 Morning**, **☀️ Afternoon**, and **🌆 Evening** activities.
   - Local delicacies checklist and practical regional travel tips.
6. **Smart Budget Overview**:
   - 4-card financial breakdown: **🚗 Transport & Transit**, **🏨 Lodging & Stay**, **🍛 Food & Dining**, and **🎫 Sightseeing & Activities**.
   - Total estimated expenses vs allocated budget with remaining buffer calculation.
7. **"My Plan Changed" Adaptive Replanning**:
   - Executive card layout handling:
     - 🌧️ *Heavy Rain / Monsoon Alert*
     - ⏰ *Transport Delay (3+ hours)*
     - 🔒 *Attraction / Monument Closure*
     - 😴 *Tired Travellers (Low-stamina leisure mode)*
     - 💰 *Budget Constraint*
   - Displays **❌ Postponed / Cancelled Activities** and **✅ Adapted Alternatives** in two visually distinct columns with AI rationale.
8. **Professional Footer**:
   - Brand name, tagline *"Explore More. Worry Less."*, Karnataka state motto, and 24/7 traveler helplines.

---

## 🔑 How to Configure Your Gemini API Key

You can configure your free Google Gemini API key using any of the following three options:

### Option 1: In the Web Browser (Easiest & Quickest)
1. Launch the app (`python -m streamlit run app.py`).
2. Open the **left sidebar** under **"🔑 Gemini AI Configuration"**.
3. Paste your Gemini API key into the **"Enter Gemini API Key"** field.
4. Click **"🚀 Generate My Itinerary"**!

### Option 2: Using `.streamlit/secrets.toml` (Recommended for Local Dev)
In the project folder, create `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "AIzaSy..."
```

### Option 3: Using Environment Variable
In your PowerShell terminal before launching:
```powershell
$env:GEMINI_API_KEY="AIzaSy..."
```

---

## 🚀 How to Run the Website

### Step 1: Open Terminal / Command Prompt
```powershell
cd "c:\AI plannar for karnataka"
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Launch the Application
```powershell
python -m streamlit run app.py
```

### Step 4: Open in Your Browser
```
http://localhost:8501
```

---

## 🧪 Testing the Integration
```powershell
python test_app.py
```
All 6 unit and integration test cases verify model ID `gemini-3.8-flash`, Pydantic schema validation, budget breakdown logic, and credential masking.
