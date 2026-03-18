import streamlit as st
from groq import Groq
import os

# ---------- PAGE ----------
st.set_page_config(
    page_title="NivasAI",
    page_icon="🏠",
    layout="wide"
)

# ---------- STATE ----------
if "search_done" not in st.session_state:
    st.session_state.search_done=False

if "messages" not in st.session_state:
    st.session_state.messages=[
        {"role":"system","content":"You are an Indian Real Estate advisor."}
    ]

import base64

def get_cursor():
    with open("cursor.cur","rb") as f:
        return base64.b64encode(f.read()).decode()

cursor_base64 = get_cursor()

def get_img():
    with open("background.png","rb") as f:
        return base64.b64encode(f.read()).decode()

bg_img=get_img()

# ---------- UI STYLE ----------

st.markdown(f"""
<style>

/* ---------- BACKGROUND ---------- */

.stApp {{

background:
linear-gradient(
rgba(2,6,23,.90),
rgba(2,6,23,.96)
),

url("data:image/jpg;base64,{bg_img}");

background-size:cover;

background-position:center;

background-repeat:no-repeat;

}}

/* ---------- CURSOR ---------- */

html, body, div {{

cursor:url("data:image/x-icon;base64,{cursor_base64}") 10 10, auto !important;

}}

button, a {{

cursor:url("data:image/x-icon;base64,{cursor_base64}") 10 10, pointer !important;

}}

input, textarea {{

cursor:text !important;

}}

/* ------- RISK BAR ------------- */

.risk-bar{{

height:10px;

background:rgba(30,41,59,.6);

border-radius:10px;

overflow:hidden;

margin-top:8px;

}}

.risk-fill{{

height:100%;

border-radius:10px;

transition: width 1.2s ease;

box-shadow:
0 0 12px rgba(99,102,241,.5);

}}

/* ---------- SIDEBAR ---------- */

[data-testid="stSidebar"] {{

background:
linear-gradient(
180deg,
#020617,
#0f172a
);

border-right:1px solid rgba(99,102,241,.15);

}}

/* ---------- CARDS ---------- */

.metric-card {{

background:
linear-gradient(
180deg,
rgba(30,41,59,.6),
rgba(15,23,42,.8)
);

padding:16px;

border-radius:16px;

border:1px solid rgba(99,102,241,.15);

box-shadow:
0 10px 25px rgba(0,0,0,.4);

transition:.25s;

}}

.metric-card:hover {{

transform:translateY(-2px);

border:1px solid rgba(99,102,241,.35);

box-shadow:
0 15px 30px rgba(99,102,241,.2);

}}

/* ---------- LOGO ---------- */

img {{

object-fit:contain;

}}

/* ---------- TYPOGRAPHY ---------- */

h1 {{

font-size:30px;

margin-bottom:0;

}}

h2 {{

font-size:18px;

}}

h3 {{

font-size:16px;

}}

p {{

font-size:13px;

color:#cbd5f5;

}}

/* ---------- ALERT BOX ---------- */

[data-testid="stAlert"] {{

background:rgba(30,58,138,.35);

border-radius:14px;

border:1px solid rgba(59,130,246,.25);

}}

</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------

st.markdown("""
<style>

.header{
display:flex;
align-items:center;
gap:15px;
margin-bottom:5px;
}

.header-title{

font-size:34px;

font-weight:700;

background:linear-gradient(
90deg,
#38bdf8,
#6366f1
);

-webkit-background-clip:text;

color:transparent;

}

.tagline{

color:#94a3b8;

font-size:14px;

margin-top:-6px;

}

</style>
""", unsafe_allow_html=True)


col_logo, col_title = st.columns([1,15])

with col_logo:
    st.image("logo.png", width=70)

with col_title:

    st.markdown(
        '<div class="header-title">NivasAI</div>',
        unsafe_allow_html=True
    )

st.markdown(
    '<div class="tagline">AI Property Decision Engine</div>',
    unsafe_allow_html=True
)

# ---------- GROQ ----------

import os

api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("API key not configured")
    st.stop()

client = Groq(api_key=api_key)
# ---------- SIDEBAR ----------

st.sidebar.title("🔍 Property Filters")

city=st.sidebar.selectbox(
"City",
["Patna","Munger","Chennai","Hyderabad","Vishakhapatnam",,"Prayagraj","Coimbatore","Ayodhya","Delhi NCR","Mumbai","Bangalore","Pondicherry","Neemrana"]
)

budget=st.sidebar.slider(
"Budget (Lakhs)",
10,
200,
25
)

bhk=st.sidebar.selectbox(
"BHK",
["1","2","3"]
)

st.sidebar.markdown("---")

st.sidebar.title("💰 Loan Calculator")

loan=st.sidebar.number_input(
"Loan Amount (in Lakhs)",
10,
200,
25
)

rate=st.sidebar.number_input(
"Interest %",
6.0,
12.0,
8.5
)

years=st.sidebar.number_input(
"Years",
5,
30,
20
)

emi=(loan*100000*(rate/1200)*(1+rate/1200)**(years*12))/((1+rate/1200)**(years*12)-1)

st.sidebar.success(
f"EMI ₹{int(emi)}"
)

salary=st.sidebar.number_input(
"Monthly Salary",
20000,
500000,
60000
)

emi_ratio=emi/salary

# ---------- SEARCH ----------

if st.sidebar.button("🔍 Analyze Property"):

    st.session_state.search_done=True

    r=client.chat.completions.create(

    model="llama-3.3-70b-versatile",

    messages=[

    {"role":"system",
    "content":"Indian property advisor"},

    {"role":"user",
    "content":f"{city} {budget} lakh"}
    ]
    )

    st.session_state.ai=r.choices[0].message.content

if not st.session_state.search_done:

    st.info("👈 Select filters and click Analyze")

    st.stop()

# ---------- DECISION ENGINE ----------

score = 10

# EMI stress scoring
if emi_ratio > 0.55:
    score -= 5

elif emi_ratio > 0.45:
    score -= 3

elif emi_ratio > 0.35:
    score -= 2

elif emi_ratio > 0.25:
    score -= 1

# Budget realism
if budget > (salary*12)/2:
    score -= 1

# Clamp score
score = max(1,min(score,10))

score=max(1,min(score,10))

risk=int(min(emi_ratio*100,100))

if risk<30:

    risk_color="#22c55e"
    risk_label="Low"

elif risk<50:

    risk_color="#eab308"
    risk_label="Moderate"

else:

    risk_color="#ef4444"
    risk_label="High"

# BUY RENT

if emi_ratio<.3:

    buy="BUY"
    buy_color="#22c55e"

elif emi_ratio<.45:

    buy="HOLD"
    buy_color="#eab308"

else:

    buy="RENT"
    buy_color="#ef4444"

# ---------- TOP ROW ----------

c1,c2,c3=st.columns([2,1,1])

with c1:

    st.markdown("### 🧠 AI Analysis")

    st.write(st.session_state.ai)

with c2: 

    if score >= 8:
        score_color = "#22c55e"   # green
        score_label = "Strong"

    elif score >=5:
        score_color = "#f59e0b"   # amber
        score_label = "Balanced"

    else:
        score_color = "#ef4444"   # red
        score_label = "Risky"


    st.markdown(f"""
    <div class="metric-card">

    <h3>Decision Score</h3>

    <h1 style="
    font-size:42px;
    color:{score_color};
    font-weight:700;
    margin-bottom:5px;
    ">

    {score}/10

    </h1>

    <p style="
    color:{score_color};
    font-weight:600;
    ">

    {score_label} Position

    </p>
    </div>
    """,unsafe_allow_html=True)

with c3:

    st.markdown(f"""
    <div class="metric-card">

    <h3>Buy vs Rent</h3>

    <h2 style="color:{buy_color}">

    {buy}

    </h2>

    </div>
    """,unsafe_allow_html=True)

# ---------- SECOND ROW ----------

c4,c5,c6=st.columns(3)

with c4:

    st.markdown("""
    <div class="metric-card">

    <h3>Affordability</h3>

    <p>EMI ₹"""+str(int(emi))+"""</p>

    </div>
    """,unsafe_allow_html=True)

with c5:

    st.markdown(f"""

    <div class="metric-card">

    <h3>Risk Indicator</h3>

    <p style="color:#94a3b8;">
    {risk_label} Risk • {risk}%
    </p>

    <div class="risk-bar">

    <div class="risk-fill"
    style="
    width:{risk}%;
    background:{risk_color};
    ">

    </div>

    </div>

    </div>

    """,unsafe_allow_html=True)

with c6:

    st.markdown("""
    <div class="metric-card">

    <h3>Decision Factors</h3>

    <p>✔ EMI check</p>

    <p>✔ Budget fit</p>

    <p>⚠ Growth varies</p>

    </div>
    """,unsafe_allow_html=True)

# ---------- PLATFORMS ----------

c7,c8,c9=st.columns(3)

with c7:
    st.link_button("MagicBricks",
    "https://magicbricks.com")

with c8:
    st.link_button("99acres",
    "https://99acres.com")

with c9:
    st.link_button("Housing",
    "https://housing.com")

# ---------- CHAT ----------

st.markdown("### 💬 Ask NivasAI")

user=st.chat_input("Ask property questions")

if user:

    st.session_state.messages.append(
    {"role":"user","content":user}
    )

    r=client.chat.completions.create(

    model="llama-3.3-70b-versatile",

    messages=st.session_state.messages
    )

    reply=r.choices[0].message.content

    st.session_state.messages.append(

    {"role":"assistant","content":reply}

    )

    st.write(reply)
