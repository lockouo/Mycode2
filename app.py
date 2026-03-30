import streamlit as st
import random
from openai import OpenAI

# ==========================================
# 1. 全局配置与绝对居中 UI 系统
# ==========================================
st.set_page_config(page_title="沉浸式赛博塔罗 | 终极完美版", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* 全局暗黑神秘学风格 */
    .stApp { background-color: #090a0f; color: #d1d5db; font-family: 'Times New Roman', STSong, serif; }
    h1, h2, h3 { color: #eab308 !important; text-align: center; text-shadow: 0 0 10px rgba(234, 179, 8, 0.3); }
    
    /* 【终极修复 1：绝对物理居中所有按钮】 */
    div.stButton {
        display: flex !important; 
        justify-content: center !important; 
        width: 100% !important;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    div.stButton > button {
        width: 220px !important; /* 固定一个美观的宽度 */
        margin: 0 auto !important; /* 物理强制居中 */
        background: transparent; border: 1px solid #eab308; color: #eab308;
        border-radius: 4px; transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 1px;
    }
    div.stButton > button:hover { 
        background: rgba(234, 179, 8, 0.1); box-shadow: 0 0 15px rgba(234, 179, 8, 0.4); border-color: #facc15; color: #facc15; 
    }

    /* 强制所有列的内容居中排列 */
    [data-testid="column"] {
        display: flex; flex-direction: column; align-items: center;
    }

    /* 核心卡槽布局 */
    .card-slot {
        display: flex; flex-direction: column; align-items: center; justify-content: flex-start;
        width: 100%;
    }
    
    /* 主牌实体与翻转特效 */
    .tarot-frame { width: 170px; height: 290px; perspective: 1000px; margin-bottom: 15px; }
    .tarot-inner { width: 100%; height: 100%; position: relative; transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }
    .is-reversed .tarot-inner { transform: rotate(180deg); } /* 逆位翻转 */
    
    .tarot-front, .tarot-back {
        width: 100%; height: 100%; position: absolute; backface-visibility: hidden;
        border-radius: 8px; box-shadow: 0 10px 25px rgba(0,0,0,0.8); border: 2px solid #4b5563;
    }
    .tarot-back {
        background: radial-gradient(circle, #1f2937 0%, #030712 100%); border-color: #eab308;
        display: flex; justify-content: center; align-items: center;
        background-image: repeating-linear-gradient(45deg, rgba(234, 179, 8, 0.05) 0, rgba(234, 179, 8, 0.05) 2px, transparent 2px, transparent 8px);
    }
    .tarot-back::after { content: '✧'; color: #eab308; font-size: 45px; opacity: 0.5; }
    .tarot-front img { width: 100%; height: 100%; object-fit: cover; border-radius: 6px; }
    
    /* 主牌百科数据看板 */
    .wiki-panel {
        width: 100%; max-width: 340px; background: rgba(17, 24, 39, 0.8);
        border: 1px solid #374151; border-top: 3px solid #eab308; border-radius: 6px;
        padding: 15px; font-size: 13px; line-height: 1.6; text-align: left; margin-bottom: 15px;
    }
    .wiki-panel.rev-panel { border-top-color: #ef4444; }
    .wiki-title { font-size: 16px; color: #f3f4f6; font-weight: bold; text-align: center; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid #374151; }
    
    /* 标签与排版 */
    .status-badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; margin-bottom: 10px; }
    .up-badge { background: rgba(34, 197, 94, 0.1); color: #4ade80; border: 1px solid #22c55e; }
    .rev-badge { background: rgba(239, 68, 68, 0.1); color: #f87171; border: 1px solid #ef4444; }
    
    .wiki-row { margin-bottom: 4px; }
    .wiki-label { color: #9ca3af; font-weight: bold; }
    .wiki-value { color: #d1d5db; }
    .wiki-highlight { color: #eab308; font-weight: bold;}
    
    /* 辅牌横向信息流图文排版 */
    .minor-card-container {
        display: flex; align-items: stretch; background: rgba(255,255,255,0.03); 
        border-radius: 6px; padding: 8px; margin-bottom: 8px; border-left: 3px solid #6b7280;
        width: 100%; max-width: 340px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); text-align: left;
    }
    .minor-img-wrapper { width: 60px; flex-shrink: 0; margin-right: 12px; perspective: 500px;}
    .minor-img-wrapper img { width: 100%; border-radius: 4px; border: 1px solid #4b5563; }
    .minor-text { font-size: 12px; line-height: 1.4; display: flex; flex-direction: column; justify-content: center;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 塔罗图鉴数据库
# ==========================================
BASE_IMG_URL = "https://sacred-texts.com/tarot/pkt/img/"

MAJORS_DB = {
    "愚者 (The Fool)": {"astro": "天王星", "elem": "风", "tags": "开始、冒险、天真、潜能、自由", "meaning": "象征着一段新旅程的开始，不计后果地跃入未知，充满无限潜能与乐观精神。"},
    "魔术师 (The Magician)": {"astro": "水星", "elem": "风", "tags": "创造、沟通、行动、资源、掌控", "meaning": "代表将内心理念化为现实的能力，手中握有四大