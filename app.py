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
    
    /* 绝对物理居中所有按钮 */
    div.stButton {
        display: flex !important; 
        justify-content: center !important; 
        width: 100% !important;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    div.stButton > button {
        width: 220px !important; 
        margin: 0 auto !important; 
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
    "魔术师 (The Magician)": {"astro": "水星", "elem": "风", "tags": "创造、沟通、行动、资源、掌控", "meaning": "代表将内心理念化为现实的能力，手中握有四大元素的资源，是绝佳的行动与沟通时机。"},
    "女祭司 (The High Priestess)": {"astro": "月亮", "elem": "水", "tags": "直觉、潜意识、神秘、等待、智慧", "meaning": "指向内在的智慧与隐秘的真相。建议在此刻保持静默，倾听直觉，向内探索而非向外寻求。"},
    "皇后 (The Empress)": {"astro": "金星", "elem": "土", "tags": "丰盛、孕育、母性、自然、感官", "meaning": "象征着物质与情感的双重丰收，充满爱与滋养的能量，代表创造力的结晶与生活的享受。"},
    "皇帝 (The Emperor)": {"astro": "白羊座", "elem": "火", "tags": "权力、秩序、规则、权威、稳定", "meaning": "代表着建立秩序与掌控全局的权威力量。需要运用理性、纪律与领导力来稳固现实基础。"},
    "教皇 (The Hierophant)": {"astro": "金牛座", "elem": "土", "tags": "信仰、传统、教育、指引、体制", "meaning": "象征精神层面的导师或传统的社会结构。暗示遵循既定规则，或寻求专业人士/长辈的指导。"},
    "恋人 (The Lovers)": {"astro": "双子座", "elem": "风", "tags": "选择、结合、爱情、价值观、和谐", "meaning": "不仅代表浪漫的情感结合，更深层意味着在重大人生分岔路口，基于真实内心的价值观抉择。"},
    "战车 (The Chariot)": {"astro": "巨蟹座", "elem": "水", "tags": "意志、胜利、控制、前进、克服", "meaning": "凭借强大的意志力与自律，控制相互冲突的力量，克服重重阻碍，最终获得物质层面的胜利。"},
    "力量 (Strength)": {"astro": "狮子座", "elem": "火", "tags": "勇气、耐心、柔克刚、内在力量", "meaning": "并非肉体的蛮力，而是以内在的勇气、爱与耐心，温柔地驯服内心的恐惧与野兽。"},
    "隐士 (The Hermit)": {"astro": "处女座", "elem": "土", "tags": "孤独、反思、沉淀、内心指引", "meaning": "暂时脱离外界喧嚣，独自踏上寻找灵魂真理的旅程。代表深度思考、谨慎与自我启蒙。"},
    "命运之轮 (Wheel of Fortune)": {"astro": "木星", "elem": "火", "tags": "转折、周期、机遇、不可抗力", "meaning": "象征宇宙法则的运转与命运的交替。低谷必将反弹，顺应时代的洪流，抓住突如其来的转机。"},
    "正义 (Justice)": {"astro": "天秤座", "elem": "风", "tags": "公平、理性、因果、法律、决断", "meaning": "代表客观公正的评判与因果法则。你的决策将带来相应的后果，要求你保持理智与平衡。"},
    "倒吊人 (The Hanged Man)": {"astro": "海王星", "elem": "水", "tags": "牺牲、换位思考、暂停、顿悟", "meaning": "通过自愿的牺牲或停滞，换取全新的视角与精神层面的顿悟。是以退为进的智慧。"},
    "死神 (Death)": {"astro": "天蝎座", "elem": "水", "tags": "结束、蜕变、新生、断舍离", "meaning": "并非肉体的死亡，而是旧有模式、关系或阶段的彻底终结，从而为全新的生命腾出空间。"},
    "节制 (Temperance)": {"astro": "射手座", "elem": "火", "tags": "平衡、调和、疗愈、中庸、结合", "meaning": "将截然不同的元素完美融合，达到动态的平衡。代表情绪的稳定、自我疗愈与妥协的艺术。"},
    "恶魔 (The Devil)": {"astro": "摩羯座", "elem": "土", "tags": "欲望、束缚、物质、成瘾、阴暗面", "meaning": "象征被物质欲望、不良习惯或有害关系所囚禁。但这种枷锁往往是自己套上的，唯有觉醒方能解脱。"},
    "高塔 (The Tower)": {"astro": "火星", "