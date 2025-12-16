import streamlit as st
import time
from datetime import datetime, timedelta
from typing import cast
from models import SessionLocal, Todo, PomodoroSession

# Sayfa Ayarları
st.set_page_config(page_title="pomozero", page_icon="✓", layout="centered")

# Veritabanı Oturumu
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Session State Initialization
if 'mode' not in st.session_state:
    st.session_state.mode = 'pomodoro'
if 'pomodoro_time' not in st.session_state:
    st.session_state.pomodoro_time = 25 * 60
if 'short_break_time' not in st.session_state:
    st.session_state.short_break_time = 5 * 60
if 'long_break_time' not in st.session_state:
    st.session_state.long_break_time = 15 * 60
if 'timer_running' not in st.session_state:
    st.session_state.timer_running = False
if 'current_time' not in st.session_state:
    st.session_state.current_time = 25 * 60
if 'session_number' not in st.session_state:
    st.session_state.session_number = 1
if 'active_session_id' not in st.session_state:
    st.session_state.active_session_id = None
if 'session_start_time' not in st.session_state:
    st.session_state.session_start_time = None
if 'show_report_modal' not in st.session_state:
    st.session_state.show_report_modal = False

# --- Pomofocus CSS Styling with Galaxy Background ---
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Galaxy Background - Pure CSS */
    .stApp {
        background: radial-gradient(ellipse at 50% 50%, #e85555 0%, #d95550 40%, #8b2320 100%);
        background-attachment: fixed;
        position: relative;
    }
    
    /* Yıldız Efekti */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(1px 1px at 20% 30%, white, rgba(255, 255, 255, 0)),
            radial-gradient(1px 1px at 60% 70%, white, rgba(255, 255, 255, 0)),
            radial-gradient(1.5px 1.5px at 50% 50%, white, rgba(255, 255, 255, 0)),
            radial-gradient(1px 1px at 80% 10%, white, rgba(255, 255, 255, 0)),
            radial-gradient(2px 2px at 90% 60%, white, rgba(255, 255, 255, 0)),
            radial-gradient(1px 1px at 30% 80%, white, rgba(255, 255, 255, 0)),
            radial-gradient(1px 1px at 10% 40%, white, rgba(255, 255, 255, 0)),
            radial-gradient(1.5px 1.5px at 40% 90%, white, rgba(255, 255, 255, 0)),
            radial-gradient(1px 1px at 70% 20%, white, rgba(255, 255, 255, 0)),
            radial-gradient(2px 2px at 15% 60%, white, rgba(255, 255, 255, 0)),
            radial-gradient(1px 1px at 85% 85%, white, rgba(255, 255, 255, 0)),
            radial-gradient(1px 1px at 45% 30%, white, rgba(255, 255, 255, 0)),
            radial-gradient(1.5px 1.5px at 75% 75%, white, rgba(255, 255, 255, 0));
        background-size: 200% 200%;
        background-position: 0% 0%;
        background-repeat: repeat;
        z-index: 0;
        pointer-events: none;
        animation: twinkle 8s infinite ease-in-out;
    }
    
    @keyframes twinkle {
        0%, 100% { opacity: 0.7; }
        50% { opacity: 1; }
    }
    
    /* Breathing animation for cat image */
    @keyframes breathing {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.03); }
    }
    
    /* Content Layer */
    .stAppViewContainer {
        z-index: 10 !important;
        position: relative;
    }
    
    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hide element IDs */
    [data-testid] {
        position: relative;
    }
    
    [data-testid]::before {
        display: none !important;
    }
    
    /* Top Navigation Bar */
    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 40px;
        color: white;
    }
    
    .logo {
        font-size: 24px;
        font-weight: 600;
        color: white;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 20px;
    }
    
    /* Timer Display */
    .timer-display {
        font-size: 120px;
        font-weight: 700;
        color: white;
        margin: 20px 0;
        font-family: 'Arial', sans-serif;
        text-align: center;
    }
    
    /* Coffee Cup Container */
    .coffee-container {
        position: relative;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin: 40px auto;
    }
    
    .coffee-svg-wrapper {
        position: relative;
        width: 280px;
        height: 250px;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .coffee-svg {
        width: 100%;
        height: auto;
        position: absolute;
    }
    
    /* Kahve dalgalanma animasyonu - smooth ve organic */
    .coffee-fill {
        animation: wave 5s ease-in-out infinite;
    }
    
    @keyframes wave {
        0% { transform: translateY(0) translateX(0); }
        25% { transform: translateY(-4px) translateX(2px); }
        50% { transform: translateY(0) translateX(0); }
        75% { transform: translateY(4px) translateX(-2px); }
        100% { transform: translateY(0) translateX(0); }
    }
    
    .timer-in-cup {
        font-size: 64px;
        font-weight: 700;
        color: #5d4037;
        z-index: 10;
        position: relative;
        margin-top: 20px;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.3);
    }
    
    /* Steam Animation */
    .steam {
        fill: none;
        stroke: #a89080;
        stroke-width: 3;
        stroke-linecap: round;
        opacity: 0;
        animation: rise 3s infinite ease-out;
    }
    
    .steam:nth-child(1) { animation-delay: 0s; }
    .steam:nth-child(2) { animation-delay: 1s; }
    .steam:nth-child(3) { animation-delay: 2s; }
    
    @keyframes rise {
        0% { transform: translateY(0); opacity: 0; }
        50% { opacity: 0.7; }
        100% { transform: translateY(-25px); opacity: 0; }
    }
    
    .coffee-status {
        text-align: center;
        color: #5d4037;
        font-size: 20px;
        margin-top: 20px;
        font-weight: 500;
    }
    
    /* Start Button - Glassmorphism */
    .stButton > button {
        background: rgba(255, 255, 255, 0.15) !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        padding: 12px 16px !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
        white-space: nowrap !important;
    }
    
    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.25) !important;
        border-color: rgba(255, 255, 255, 0.5) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Coffee Mode Button Color - Glassmorphism */
    .coffee-btn button {
        background: rgba(93, 64, 55, 0.15) !important;
        color: #fdf6e3 !important;
        border: 1px solid rgba(93, 64, 55, 0.3) !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08) !important;
    }
    
    .coffee-btn button:hover {
        background: rgba(93, 64, 55, 0.25) !important;
        border-color: rgba(93, 64, 55, 0.5) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12) !important;
    }
    
    /* Session Info */
    .session-info {
        color: white;
        font-size: 20px;
        margin: 30px 0;
        font-weight: 300;
        text-align: center;
    }
    
    /* Tasks Section */
    .tasks-header {
        color: white;
        font-size: 20px;
        font-weight: 700;
        margin: 40px 0 20px 0;
        text-align: center;
        border-bottom: 2px solid rgba(255, 255, 255, 0.4);
        padding-bottom: 10px;
    }
    
    .task-item {
        color: white !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        margin: 0 !important;
        padding: 8px 0 !important;
        line-height: 1.5 !important;
    }
    
    .task-completed {
        text-decoration: line-through;
        opacity: 0.6;
        color: white !important;
        margin: 0 !important;
        padding: 8px 0 !important;
        line-height: 1.5 !important;
    }
    
    /* Checkbox alignment */
    .stCheckbox {
        margin: 0 !important;
        padding: 8px 0 !important;
    }
    
    .stCheckbox > label {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Coffee Mode Specific */
    .coffee-container {
        position: relative;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin: 40px auto;
    }
    
    .coffee-svg-wrapper {
        position: relative;
        width: 280px;
        height: 250px;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .coffee-svg {
        width: 100%;
        height: auto;
        position: absolute;
    }
    
    .timer-in-cup-global {
        font-size: 52px;
        font-weight: 900;
        color: #5d4037;
        z-index: 10;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-shadow: 1px 1px 2px rgba(255,255,255,0.3);
    }
    
    .steam-path {
        fill: none;
        stroke: #a89080;
        stroke-width: 3;
        stroke-linecap: round;
        opacity: 0;
        animation: riseUp 3s infinite ease-out;
    }
    
    .steam-path:nth-child(2) { animation-delay: 0s; }
    .steam-path:nth-child(3) { animation-delay: 1s; }
    .steam-path:nth-child(4) { animation-delay: 2s; }
    
    @keyframes riseUp {
        0% { transform: translateY(0); opacity: 0; }
        50% { opacity: 0.7; }
        100% { transform: translateY(-15px); opacity: 0; }
    }
    
    .coffee-status {
        text-align: center;
        color: #5d4037;
        font-size: 20px;
        margin-top: 20px;
        font-weight: 500;
    }
    
    /* Center content */
    .block-container {
        max-width: 600px;
        padding-top: 1rem;
    }
    
    /* Input field styling - Glassmorphism */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #000 !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
        padding: 12px 16px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(0, 0, 0, 0.5) !important;
    }
    
    .stTextInput > div > div > input:focus {
        background-color: rgba(255, 255, 255, 0.15) !important;
        border-color: rgba(255, 255, 255, 0.4) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stTextInput label {
        color: white !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    
    .stExpander {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
        overflow: hidden !important;
    }
    
    .stExpander > div > button {
        color: white !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stExpander > div > button:hover {
        background-color: rgba(255, 255, 255, 0.1) !important;
    }
    
    .stInfo {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stInfo > div > div {
        color: white !important;
        font-weight: 500 !important;
    }
    
    /* Info message custom class */
    .info-message {
        color: white;
        font-weight: 500;
        font-size: 15px;
        text-align: center;
        padding: 20px;
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    /* Türkçeleştir form submit hint */
    form small {
        font-size: 0 !important;
    }
    
    form small::after {
        content: 'Enter tuşu ile gönder';
        font-size: 12px !important;
        color: rgba(255, 255, 255, 0.6) !important;
    }
    
    /* Glassmorphism Modal System */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(20px);
        z-index: 9999;
        display: flex;
        justify-content: center;
        align-items: center;
        animation: fadeIn 0.3s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes modalSlide {
        from { 
            opacity: 0;
            transform: scale(0.95) translateY(20px);
        }
        to { 
            opacity: 1;
            transform: scale(1) translateY(0);
        }
    }
    
    .modal-content {
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(40px);
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 24px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.1) inset;
        padding: 40px;
        max-width: 900px;
        width: 90%;
        max-height: 85vh;
        overflow-y: auto;
        position: relative;
        animation: modalSlide 0.4s ease-out;
    }
    
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 30px;
        padding-bottom: 20px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .modal-title {
        font-size: 32px;
        font-weight: 700;
        color: white;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .modal-close {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        color: white;
        font-size: 24px;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
    }
    
    .modal-close:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: rotate(90deg);
    }
    
    /* KPI Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }
    
    .kpi-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .kpi-card:hover {
        background: rgba(255, 255, 255, 0.12);
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
    }
    
    .kpi-value {
        font-size: 42px;
        font-weight: 700;
        color: white;
        margin-bottom: 8px;
    }
    
    .kpi-label {
        font-size: 14px;
        color: rgba(255, 255, 255, 0.7);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Stats Section */
    .stats-section {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }
    
    .stats-section h3 {
        color: white;
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 16px;
    }
    
    .stat-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        color: rgba(255, 255, 255, 0.9);
    }
    
    .stat-row:last-child {
        border-bottom: none;
    }
    
    .stat-label {
        font-size: 15px;
    }
    
    .stat-value {
        font-size: 16px;
        font-weight: 600;
    }
    
    /* Coffee Mode Modal Styling */
    .coffee-modal .modal-content {
        background: rgba(253, 246, 227, 0.15);
    }
    
    .coffee-modal .modal-title,
    .coffee-modal .kpi-value,
    .coffee-modal .stat-row,
    .coffee-modal .stats-section h3 {
        color: #5d4037 !important;
    }
    
    .coffee-modal .kpi-label,
    .coffee-modal .stat-label {
        color: rgba(93, 64, 55, 0.7) !important;
    }
    
    .coffee-modal .modal-close {
        color: #5d4037;
    }
    
    /* Scrollbar for modal */
    .modal-content::-webkit-scrollbar {
        width: 8px;
    }
    
    .modal-content::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    
    .modal-content::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
    }
    
    .modal-content::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.3);
    }
    
    /* Glass Panel - Optimal Glassmorphism */
    .glass-panel {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        padding: 24px;
    }
    
    .glass-panel:hover {
        background: rgba(255, 255, 255, 0.15);
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.15);
    }
    
</style>
""", unsafe_allow_html=True)

# Kahve molası modunda arka plan rengini değiştir
if st.session_state.mode == 'coffee_break':
    st.markdown("""
    <style>
        .stApp {
            background: radial-gradient(ellipse at 50% 50%, #fdf6e3 0%, #f5ede3 50%, #e8dcc8 100%);
            background-attachment: fixed;
        }
        
        .stApp::before {
            display: none !important;
        }
        
        .logo {
            color: #5d4037 !important;
        }
        
        .top-nav, .logo, .session-info, .tasks-header {
            color: #5d4037 !important;
        }
        
        .tasks-header {
            border-bottom-color: rgba(93, 64, 55, 0.3) !important;
        }
        
        /* Coffee Mode Glassmorphism Buttons */
        .stButton > button {
            background: rgba(93, 64, 55, 0.12) !important;
            color: #5d4037 !important;
            border: 1px solid rgba(93, 64, 55, 0.25) !important;
            backdrop-filter: blur(10px) !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06) !important;
        }
        
        .stButton > button:hover {
            background: rgba(93, 64, 55, 0.18) !important;
            border-color: rgba(93, 64, 55, 0.4) !important;
            transform: translateY(-2px) !important;
        }
        
        /* Coffee Mode Input - Glassmorphism */
        .stTextInput > div > div > input {
            background-color: rgba(93, 64, 55, 0.08) !important;
            color: #5d4037 !important;
            border: 1px solid rgba(93, 64, 55, 0.2) !important;
            backdrop-filter: blur(10px) !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: rgba(93, 64, 55, 0.5) !important;
        }
        
        .stTextInput > div > div > input:focus {
            background-color: rgba(93, 64, 55, 0.12) !important;
            border-color: rgba(93, 64, 55, 0.35) !important;
        }
        
        .stTextInput label {
            color: #5d4037 !important;
        }
        
        /* Coffee Mode Expander - Glassmorphism */
        .stExpander {
            background-color: rgba(93, 64, 55, 0.08) !important;
            border: 1px solid rgba(93, 64, 55, 0.2) !important;
        }
        
        .stExpander > div > button {
            color: #5d4037 !important;
        }
        
        .stExpander > div > button:hover {
            background-color: rgba(93, 64, 55, 0.1) !important;
        }
        
        /* Coffee Mode Info - Glassmorphism */
        .stInfo {
            background-color: rgba(93, 64, 55, 0.08) !important;
            border: 1px solid rgba(93, 64, 55, 0.2) !important;
        }
        
        .stInfo > div > div {
            color: #5d4037 !important;
        }
        
        /* Coffee Mode Info Message */
        .info-message {
            color: #5d4037 !important;
            background-color: rgba(93, 64, 55, 0.08) !important;
            border: 1px solid rgba(93, 64, 55, 0.2) !important;
        }
        
        /* Coffee Mode Tasks */
        .task-item {
            color: #5d4037 !important;
        }
        
        .task-completed {
            color: #5d4037 !important;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Top Navigation ---
nav_col1, nav_col2 = st.columns([3, 1])
with nav_col1:
    st.markdown('<div class="logo">✓ pomozero</div>', unsafe_allow_html=True)
with nav_col2:
    # Hide the report button during coffee break mode
    if st.session_state.mode != 'coffee_break':
        if st.button("📊 Rapor", key="report_btn", use_container_width=True):
            st.session_state.show_report_modal = True
            st.rerun()

# --- Mode Selection ---
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Pomodoro", key="pomodoro_btn", use_container_width=True):
        st.session_state.mode = 'pomodoro'
        st.session_state.current_time = st.session_state.pomodoro_time
        st.session_state.timer_running = False
        st.rerun()
with col2:
    if st.button("Kısa Mola", key="short_btn", use_container_width=True):
        st.session_state.mode = 'short_break'
        st.session_state.current_time = st.session_state.short_break_time
        st.session_state.timer_running = False
        st.rerun()
with col3:
    if st.button("Kahve Molası", key="long_btn", use_container_width=True):
        st.session_state.mode = 'coffee_break'
        st.session_state.current_time = st.session_state.long_break_time
        st.session_state.timer_running = False
        st.rerun()

# --- Timer Display ---
mins, secs = divmod(st.session_state.current_time, 60)
time_format = f'{mins:02d}:{secs:02d}'

# Kahve Molası modunda özel tasarım
if st.session_state.mode == 'coffee_break':
    # Geçen sürenin yüzdesini hesapla
    total_time = st.session_state.long_break_time
    time_elapsed = total_time - st.session_state.current_time
    percentage = (time_elapsed / total_time) * 100 if total_time > 0 else 0
    
    # Minimum %18 doluluk ile başla
    percentage = max(18, percentage)
    
    # Fincan dolum hesaplaması (SVG koordinatları)
    cup_bottom_y = 180
    cup_top_y = 50
    max_fill_height = cup_bottom_y - cup_top_y  # 130
    current_height = max_fill_height * (percentage / 100)
    current_y = cup_bottom_y - current_height
    
    coffee_status = '☕ Kahveniz demleniyor...' if st.session_state.timer_running else '✨ Kahveniz hazır! Afiyet olsun.'
    
    # Basit HTML - smooth wave için daha hassas hesaplama
    y_value = str(max(0, current_y))
    height_value = str(max(0, current_height))
    wave_y1 = str(max(0, current_y - 3))
    wave_y2 = str(max(0, current_y + 3))
    wave_mid = str(max(0, current_y))
    
    html_code = '<div class="coffee-container"><div class="coffee-svg-wrapper"><svg class="coffee-svg" viewBox="0 0 200 220" xmlns="http://www.w3.org/2000/svg"><defs><clipPath id="cup-mask"><path d="M40 50 L 160 50 L 150 160 C 150 180, 50 180, 50 160 Z" /></clipPath><clipPath id="wave-mask"><path d="M35 ' + wave_y1 + ' C 50 ' + wave_y2 + ', 60 ' + wave_y2 + ', 75 ' + wave_mid + ' S 90 ' + wave_y1 + ', 105 ' + wave_mid + ' S 130 ' + wave_y2 + ', 155 ' + wave_y1 + ' L 155 200 L 35 200 Z" /></clipPath></defs><path d="M160 80 C 195 80, 195 130, 160 130" stroke="#5d4037" stroke-width="10" fill="none" stroke-linecap="round" /><path d="M40 50 L 160 50 L 150 160 C 150 180, 50 180, 50 160 Z" fill="#efebe9" stroke="#5d4037" stroke-width="5" /><g clip-path="url(#cup-mask)"><g clip-path="url(#wave-mask)"><rect class="coffee-fill" x="35" y="' + y_value + '" width="120" height="' + height_value + '" fill="#6f4e37" /></g></g><path d="M40 50 L 160 50 L 150 160 C 150 180, 50 180, 50 160 Z" fill="none" stroke="#5d4037" stroke-width="5" /></svg><div class="timer-in-cup-global">' + time_format + '</div></div><div class="coffee-status">' + coffee_status + '</div></div>'
    
    st.markdown(html_code, unsafe_allow_html=True)
else:
    # Normal timer display (Pomodoro ve Kısa Mola için)
    st.markdown(f'<div class="timer-display">{time_format}</div>', unsafe_allow_html=True)

# --- Start/Pause Button ---
col_center = st.columns([1, 2, 1])
with col_center[1]:
    if st.session_state.mode == 'coffee_break':
        st.markdown('<div class="coffee-btn">', unsafe_allow_html=True)
    
    if st.session_state.timer_running:
        if st.button("DURAKLAT", use_container_width=True):
            st.session_state.timer_running = False
            
            # Mark session as abandoned (not completed)
            if st.session_state.active_session_id:
                db = next(get_db())
                session = db.query(PomodoroSession).filter(PomodoroSession.id == st.session_state.active_session_id).first()
                if session:
                    session.end_time = datetime.now()
                    session.actual_duration = int((datetime.now() - session.start_time).total_seconds() / 60)
                    session.completed = False
                    db.commit()
                db.close()
                st.session_state.active_session_id = None
            st.rerun()
    else:
        if st.button("BAŞLAT", use_container_width=True):
            st.session_state.timer_running = True
            st.session_state.session_start_time = datetime.now()
            
            # Create new session record in database
            db = next(get_db())
            new_session = PomodoroSession(
                session_type=st.session_state.mode,
                start_time=st.session_state.session_start_time,
                planned_duration=st.session_state.current_time,
                completed=False,
                date=datetime.now()
            )
            db.add(new_session)
            db.commit()
            st.session_state.active_session_id = new_session.id
            db.close()
            st.rerun()
    
    if st.session_state.mode == 'coffee_break':
        st.markdown('</div>', unsafe_allow_html=True)

# --- Timer Logic ---
if st.session_state.timer_running:
    if st.session_state.current_time > 0:
        time.sleep(1)
        st.session_state.current_time -= 1
        st.rerun()
    else:
        st.session_state.timer_running = False
        
        # Mark session as completed
        if st.session_state.active_session_id:
            db = next(get_db())
            session = db.query(PomodoroSession).filter(PomodoroSession.id == st.session_state.active_session_id).first()
            if session:
                session.end_time = datetime.now()
                session.actual_duration = int((datetime.now() - session.start_time).total_seconds() / 60)
                session.completed = True
                db.commit()
            db.close()
            st.session_state.active_session_id = None
        
        st.balloons()
        st.rerun()

# --- Session Info (Sadece Pomodoro ve Kısa Mola için) ---
if st.session_state.mode != 'coffee_break':
    if st.session_state.mode == 'short_break':
        st.markdown('<div class="session-info"><img src="data:image/png;base64,{}" style="width: 280px; height: 280px; margin-bottom: -100px; margin-top: -80px; border-radius: 50%; animation: breathing 3s ease-in-out infinite;"><br>Yatışşşşş (:</div>'.format(__import__('base64').b64encode(open('image/cat.png', 'rb').read()).decode()), unsafe_allow_html=True)
    else:
        st.markdown('<div class="session-info">Odaklanma zamanı!</div>', unsafe_allow_html=True)

# --- Statistics Modal ---
if st.session_state.show_report_modal:
    db = next(get_db())
    
    # Calculate statistics
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    
    # Today's stats
    today_sessions = db.query(PomodoroSession).filter(
        PomodoroSession.date >= today,
        PomodoroSession.completed == True
    ).all()
    
    # Week stats
    week_sessions = db.query(PomodoroSession).filter(
        PomodoroSession.date >= week_ago,
        PomodoroSession.completed == True
    ).all()
    
    # All time stats
    all_sessions = db.query(PomodoroSession).filter(
        PomodoroSession.completed == True
    ).all()
    
    # Calculate totals using database queries for proper filtering
    today_work_sessions = db.query(PomodoroSession).filter(
        PomodoroSession.date >= today,
        PomodoroSession.completed == True,
        PomodoroSession.session_type == 'pomodoro'
    ).all()
    today_break_sessions = db.query(PomodoroSession).filter(
        PomodoroSession.date >= today,
        PomodoroSession.completed == True,
        PomodoroSession.session_type.in_(['short_break', 'coffee_break'])
    ).all()
    today_work_mins = sum([(s.actual_duration or 0) for s in today_work_sessions]) / 60 if today_work_sessions else 0
    today_break_mins = sum([(s.actual_duration or 0) for s in today_break_sessions]) / 60 if today_break_sessions else 0
    
    week_work_sessions = db.query(PomodoroSession).filter(
        PomodoroSession.date >= week_ago,
        PomodoroSession.completed == True,
        PomodoroSession.session_type == 'pomodoro'
    ).all()
    week_break_sessions = db.query(PomodoroSession).filter(
        PomodoroSession.date >= week_ago,
        PomodoroSession.completed == True,
        PomodoroSession.session_type.in_(['short_break', 'coffee_break'])
    ).all()
    week_work_mins = sum([(s.actual_duration or 0) for s in week_work_sessions]) / 60 if week_work_sessions else 0
    week_break_mins = sum([(s.actual_duration or 0) for s in week_break_sessions]) / 60 if week_break_sessions else 0
    
    total_sessions = db.query(PomodoroSession).count()
    completed_sessions = len(all_sessions)
    completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
    # Streak calculation
    all_dates = db.query(PomodoroSession.date).filter(PomodoroSession.completed == True).distinct().order_by(PomodoroSession.date.desc()).all()
    streak = 0
    current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    for date_tuple in all_dates:
        session_date = date_tuple[0].replace(hour=0, minute=0, second=0, microsecond=0)
        if session_date == current_date:
            streak += 1
            current_date = current_date - timedelta(days=1)
        elif session_date == current_date - timedelta(days=1):
            streak += 1
            current_date = current_date - timedelta(days=1)
        else:
            break
    
    # Custom CSS for white text - STRONG
    st.markdown('''
        <style>
            .stMetric { color: white !important; }
            .stMetric > div > div { color: white !important; }
            .stMetric label { color: white !important; }
            .stMetric > div > label { color: white !important; }
            div[data-testid="metric-container"] { color: white !important; }
            div[data-testid="metric-container"] label { color: white !important; }
            div[data-testid="metric-container"] > div { color: white !important; }
            div[data-testid="metric-container"] span { color: white !important; }
            p { color: white !important; }
            h1, h2, h3, h4, h5, h6 { color: white !important; }
            
            /* Kahve molası bölümü için özel renk */
            .coffee-section { color: #5d4037 !important; }
            .coffee-section * { color: #5d4037 !important; }
            .coffee-section p { color: #5d4037 !important; }
            .coffee-section span { color: #5d4037 !important; }
            .coffee-section label { color: #5d4037 !important; }
            .coffee-section h1, .coffee-section h2, .coffee-section h3, .coffee-section h4, .coffee-section h5, .coffee-section h6 { color: #5d4037 !important; }
            .coffee-section div[data-testid="metric-container"] { color: #5d4037 !important; }
            .coffee-section div[data-testid="metric-container"] * { color: #5d4037 !important; }
            .coffee-section .stMetric { color: #5d4037 !important; }
            .coffee-section .stMetric > div > div { color: #5d4037 !important; }
        </style>
    ''', unsafe_allow_html=True)
    
    # Title
    st.markdown('<h2 style="color: white; text-align: center;">📊 İstatistikler</h2>', unsafe_allow_html=True)
    
    # Close button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("✕ Kapat", use_container_width=True, key="close_report_btn"):
            st.session_state.show_report_modal = False
            st.rerun()
    
    st.divider()
    
    # KPI row - Cast to proper types for display
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Bugün", f"{int(cast(float, today_work_mins))} dk")
    with col2:
        st.metric("Hafta", f"{int(cast(float, week_work_mins))} dk")
    with col3:
        st.metric("Tamamlama", f"{completion_rate:.0f}%")
    with col4:
        st.metric("Streak", f"{streak} 🔥")
    
    st.divider()
    st.markdown('<h3 style="color: white; text-align: center;">📅 Bugünkü Detaylar</h3>', unsafe_allow_html=True)
    
    d1, d2 = st.columns(2)
    with d1:
        st.metric("🎯 Pomodoro", len(today_work_sessions))
        st.metric("☕ Kahve", len([s for s in today_sessions if str(s.session_type) == 'coffee_break']))
    with d2:
        st.metric("⏸️ Molalar", len([s for s in today_sessions if str(s.session_type) == 'short_break']))
        st.metric("💤 Dinlenme", f"{int(cast(float, today_break_mins))} dk")
    
    st.divider()
    st.markdown('<h3 style="color: white; text-align: center;">📊 Bu Hafta</h3>', unsafe_allow_html=True)
    
    w1, w2 = st.columns(2)
    with w1:
        st.metric("📅 Günler", len(set([s.date.date() for s in week_sessions])))
    with w2:
        st.metric("⏱️ Çalışma", f"{int(cast(float, week_work_mins))} dk")
    
    st.metric("💤 Dinlenme", f"{int(cast(float, week_break_mins))} dk")
    
    st.divider()
    st.markdown('<h3 style="color: white; text-align: center;">⭐ Tüm Zamanlar</h3>', unsafe_allow_html=True)
    
    a1, a2, a3 = st.columns(3)
    with a1:
        st.metric("✅ Başarı", completed_sessions)
    with a2:
        st.metric("❌ Yarım", total_sessions - completed_sessions)
    with a3:
        st.metric("📈 Oran", f"{completion_rate:.1f}%")
    
    db.close()

# --- Tasks Section (Hidden when modal is shown) ---
if not st.session_state.show_report_modal:
    st.markdown('<div class="tasks-header">Görevler</div>', unsafe_allow_html=True)
    
    db = next(get_db())
    
    # Add Task Section
    with st.expander("➕ Görev Ekle", expanded=False):
        with st.form("add_task_form", clear_on_submit=True):
            new_task_title = st.text_input("Ne üzerinde çalışıyorsun?", placeholder="Görev adını gir...")
            submitted = st.form_submit_button("Görev Ekle", use_container_width=True)
            
            if submitted and new_task_title:
                new_todo = Todo(title=new_task_title)
                db.add(new_todo)
                db.commit()
                st.rerun()
    
    # Display Tasks
    tasks = db.query(Todo).order_by(Todo.created_at.desc()).all()
    
    if not tasks:
        st.markdown("<div class='info-message'>🎯 Görevlerini organize etmeye başlamak için 'Görev Ekle'ye tıkla</div>", unsafe_allow_html=True)
    else:
        for task in tasks:
            col_check, col_text, col_del = st.columns([0.8, 4, 1], gap="small")
            
            with col_check:
                # Get the actual boolean value from the Column object
                task_completed: bool = cast(bool, task.is_done)
                is_done = st.checkbox("✓", value=task_completed, key=f"check_{task.id}", label_visibility="collapsed")
                if is_done != task_completed:
                    task.is_done = is_done
                    db.commit()
                    st.rerun()
            
            with col_text:
                task_completed = cast(bool, task.is_done)
                task_class = 'task-completed' if task_completed else 'task-item'
                st.markdown(f"<div class='{task_class}'>{task.title}</div>", unsafe_allow_html=True)
            
            with col_del:
                if st.button("✕", key=f"del_{task.id}", help="Görev sil"):
                    db.delete(task)
                    db.commit()
                    st.rerun()
    
    db.close()
