import streamlit as st
import random
from openai import OpenAI

# ==========================================
# 1. 全局配置与高级图形化 UI 系统
# ==========================================
st.set_page_config(page_title="塔罗占卜", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* 引入深邃星空背景 */
    .stApp { 
        background-color: rgba(9, 10, 15, 0.85); 
        background-image: url('https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=1920&auto=format&fit=crop');
        background-size: cover; background-attachment: fixed; background-blend-mode: overlay;
        color: #d1d5db; font-family: 'Times New Roman', STSong, serif; 
    }
    
    [data-testid="collapsedControl"] { display: none; }
    
    /* 图形化艺术标题 */
    .header-box {
        display: flex; align-items: center; justify-content: center;
        margin-top: 50px; margin-bottom: 40px;
    }
    .header-line { height: 1px; width: 60px; background: linear-gradient(to right, transparent, #eab308); margin: 0 20px; }
    .header-line-rev { height: 1px; width: 60px; background: linear-gradient(to left, transparent, #eab308); margin: 0 20px; }
    .header-text { 
        font-size: 3rem; color: #eab308; text-shadow: 0 0 20px rgba(234, 179, 8, 0.5); 
        letter-spacing: 12px; font-weight: normal; 
    }

    /* 绝对对齐：标题与卡槽 */
    [data-testid="column"] { display: flex; flex-direction: column; align-items: center; text-align: center; }
    .stage-title {
        color: #f3f4f6 !important; font-size: 1.5rem; margin-bottom: 25px;
        display: flex; align-items: center; justify-content: center; width: 100%;
    }
    .stage-title::before, .stage-title::after { content: '✦'; color: #eab308; margin: 0 10px; font-size: 1rem; opacity: 0.7; }

    /* 按钮居中对齐修复 */
    div.stButton { display: flex !important; justify-content: center !important; width: 100% !important; margin-top: 10px; }
    div.stButton > button {
        width: 220px !important; margin: 0 auto !important; 
        background: rgba(0, 0, 0, 0.5); border: 1px solid #eab308; color: #eab308;
        border-radius: 4px; transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 1px;
    }

    .card-slot { display: flex; flex-direction: column; align-items: center; justify-content: flex-start; width: 100%; }
    .tarot-frame { width: 170px; height: 290px; perspective: 1000px; margin-bottom: 15px; }
    .tarot-inner { width: 100%; height: 100%; position: relative; transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; }
    .is-reversed .tarot-inner { transform: rotate(180deg); }
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
    
    .wiki-panel {
        width: 100%; max-width: 340px; background: rgba(17, 24, 39, 0.7); backdrop-filter: blur(5px);
        border: 1px solid #374151; border-top: 3px solid #eab308; border-radius: 6px;
        padding: 15px; font-size: 13px; line-height: 1.6; text-align: left; margin-bottom: 15px;
    }
    .wiki-panel.rev-panel { border-top-color: #ef4444; }
    .wiki-title { font-size: 16px; color: #f3f4f6; font-weight: bold; text-align: center; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid #374151; }
    
    .status-badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; margin-bottom: 10px; }
    .up-badge { background: rgba(34, 197, 94, 0.1); color: #4ade80; border: 1px solid #22c55e; }
    .rev-badge { background: rgba(239, 68, 68, 0.1); color: #f87171; border: 1px solid #ef4444; }
    
    .minor-card-container {
        display: flex; flex-direction: column; align-items: center; background: rgba(17, 24, 39, 0.6); backdrop-filter: blur(5px);
        border-radius: 8px; padding: 15px; margin-bottom: 15px; border-top: 3px solid #6b7280;
        width: 100%; max-width: 340px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); text-align: left;
    }
    .minor-img-wrapper { width: 120px; margin-bottom: 12px; perspective: 500px; box-shadow: 0 5px 15px rgba(0,0,0,0.8); border-radius: 4px;}
    .minor-img-wrapper img { width: 100%; border-radius: 4px; border: 1px solid #4b5563; }
    .minor-text { width: 100%; font-size: 13px; line-height: 1.5; }
    
    .hero-subtitle {
        color: #9ca3af; font-size: 1.1rem; text-align: center; max-width: 600px; 
        margin: 0 auto 40px auto; line-height: 1.8; letter-spacing: 1px;
    }

    /* AI 解析区域优化样式 */
    .ai-interpretation-container {
        background: linear-gradient(180deg, rgba(26, 28, 41, 0.9) 0%, rgba(9, 10, 15, 0.95) 100%);
        border: 1px solid rgba(234, 179, 8, 0.3);
        border-top: 4px solid #eab308;
        border-radius: 12px;
        padding: 40px;
        margin: 40px auto;
        max-width: 900px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.6);
        position: relative;
    }
    .ai-interpretation-container::before {
        content: '✍️';
        position: absolute;
        top: -20px;
        left: 50%;
        transform: translateX(-50%);
        background: #090a10;
        padding: 0 15px;
        font-size: 24px;
    }
    .ai-content {
        color: #e0e0e0;
        line-height: 1.85;
        font-size: 1.1rem;
        text-align: justify;
        letter-spacing: 0.5px;
    }
    .ai-content h2, .ai-content h3 {
        color: #eab308 !important;
        margin-top: 30px;
        margin-bottom: 15px;
        text-align: left !important;
        border-bottom: 1px solid rgba(234, 179, 8, 0.2);
        padding-bottom: 5px;
    }
    .ai-content p {
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 安全后台 API 读取
# ==========================================
try:
    api_base = st.secrets.get("API_BASE", "https://api.openai.com/v1")
    api_model = st.secrets.get("API_MODEL", "gpt-3.5-turbo")
    api_key = st.secrets.get("API_KEY", "")
except:
    api_base = "https://api.openai.com/v1"
    api_model = "gpt-3.5-turbo"
    api_key = ""

# ==========================================
# 3. 塔罗图鉴数据库
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
    "高塔 (The Tower)": {"astro": "火星", "elem": "火", "tags": "突变、毁灭、崩溃、意外的觉醒", "meaning": "建立在虚假基础上的事物被突然且猛烈地摧毁。虽然带来痛苦，但清除了阻碍，是痛苦却必要的觉醒。"},
    "星星 (The Star)": {"astro": "水瓶座", "elem": "风", "tags": "希望、疗愈、灵感、宁静、信仰", "meaning": "经历了高塔的毁灭后，迎来的宁静与希望。代表宇宙的祝福、灵感的涌现与精神的彻底疗愈。"},
    "月亮 (The Moon)": {"astro": "双鱼座", "elem": "水", "tags": "不安、迷茫、潜意识、欺骗、恐惧", "meaning": "深入潜意识的幽暗地带，事物晦暗不明，充满未知的恐惧与幻象。需要极大的直觉力来辨别真伪。"},
    "太阳 (The Sun)": {"astro": "太阳", "elem": "火", "tags": "快乐、成功、生命力、真相、光明", "meaning": "塔罗牌中最积极的牌之一。象征绝对的成功、纯粹的快乐、旺盛的生命力与一切阴霾的消散。"},
    "审判 (Judgement)": {"astro": "冥王星", "elem": "火", "tags": "觉醒、召唤、救赎、总结、重生", "meaning": "听到来自高我的召唤，对过去的业力进行最终清算。代表原谅过去，彻底放下，迎来精神的涅槃。"},
    "世界 (The World)": {"astro": "土星", "elem": "土", "tags": "圆满、达成、完美、旅程终点", "meaning": "愚者旅程的完美终点。代表目标的彻底达成、身心合一的圆满状态，以及准备开启下一个更高维度的循环。"}
}
suits_info = {"权杖": "wa", "圣杯": "cu", "宝剑": "sw", "星币": "pe"}
ranks_map = {
    "首牌": {"code": "ac", "desc": "潜能爆发与新契机"}, "二": {"code": "02", "desc": "选择、平衡与规划"}, 
    "三": {"code": "03", "desc": "初步成果与团队协作"}, "四": {"code": "04", "desc": "稳定、停滞与休息"},
    "五": {"code": "05", "desc": "冲突、挑战与困境"}, "六": {"code": "06", "desc": "和谐、援助与过渡"}, 
    "七": {"code": "07", "desc": "防守、坚持与勇气"}, "八": {"code": "08", "desc": "迅速发展与专注目标"},
    "九": {"code": "09", "desc": "接近顶点、独立与焦虑"}, "十": {"code": "10", "desc": "阶段完结与承受重压"}, 
    "侍从": {"code": "pa", "desc": "探索未知与新的消息"}, "骑士": {"code": "kn", "desc": "冲动与行动力爆发"},
    "王后": {"code": "qu", "desc": "内在丰盈与成熟滋养"}, "国王": {"code": "ki", "desc": "建立秩序与外在掌控"}
}
elem_map = {"权杖": "火", "圣杯": "水", "宝剑": "风", "星币": "土"}
core_map = {"权杖": "行动与创造", "圣杯": "情感与人际", "宝剑": "思想与沟通", "星币": "物质与现实"}

MAJORS = {}
for i, (name, data) in enumerate(MAJORS_DB.items()):
    MAJORS[name] = {
        "img_url": f"{BASE_IMG_URL}ar{i:02d}.jpg", "tags": data["tags"], "astro": data["astro"], "elem": data["elem"],
        "up": f"{data['meaning']}", "rev": f"警告：{data['meaning']} 能量发生扭曲、过度或遭遇阻碍。需反思。"
    }
MINORS = {}
for suit, s_code in suits_info.items():
    for rank, r_data in ranks_map.items():
        full_name = f"{suit}{rank}"
        elem = elem_map[suit]
        if full_name == "权杖首牌":
            MINORS["权杖首牌 (Ace Of Wands)"] = {
                "img_url": f"{BASE_IMG_URL}waac.jpg", "tags": "新行动、创造、机会、启动", "elem": f"{elem}元素",
                "up": "【正位】代表潜能的迸发与新机会的到来。能量十分充沛，鼓励积极行动与勇敢探索。",
                "rev": "【逆位】暗示热情消退或方向错误。能量发生失控，可能面临计划缺失及资源浪费。"
            }
        else:
            MINORS[f"{full_name}"] = {
                "img_url": f"{BASE_IMG_URL}{s_code}{r_data['code']}.jpg",
                "tags": f"{core_map[suit]}、{r_data['desc'].split('与')[0]}", "elem": f"{elem}元素",
                "up": f"【正位】代表着{r_data['desc']}。当前能量顺畅，事物正朝着积极的方向发展，宜顺势而为。",
                "rev": f"【逆位】暗示{r_data['desc']}的特质受阻或被过度放大。面临延迟与内耗，需要谨慎调整。"
            }

# ==========================================
# 4. 状态机渲染
# ==========================================
if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.deck_m = list(MAJORS.keys()); random.shuffle(st.session_state.deck_m)
    st.session_state.deck_min = list(MINORS.keys()); random.shuffle(st.session_state.deck_min)
    st.session_state.spread = {"past": {}, "present": {}, "future": {}}

def draw_card(is_major):
    return {"name": (st.session_state.deck_m if is_major else st.session_state.deck_min).pop(), "pos": random.choice(["正位", "逆位"])}

def render_slot(stage_name, step_req_major, step_req_minor, state_key):
    st.markdown(f"<div class='stage-title'>{stage_name}</div>", unsafe_allow_html=True)
    
    if st.session_state.step < step_req_major:
        st.markdown("""
        <div class="card-slot">
            <div class="tarot-frame"><div class="tarot-inner"><div class="tarot-back"></div></div></div>
            <div style="color:#9ca3af; font-size:12px; margin-top:10px; margin-bottom:10px;">[ 命运尚未揭晓 ]</div>
        </div>
        """, unsafe_allow_html=True)
        if st.session_state.step == step_req_major - 1:
            if st.button(f"揭开 {stage_name} 主牌", key=f"btn_m_{stage_name}", use_container_width=True):
                st.session_state.spread[state_key]["major"] = draw_card(True)
                st.session_state.step = step_req_major; st.rerun()
                
    if st.session_state.step >= step_req_major:
        card = st.session_state.spread[state_key]["major"]
        data = MAJORS[card["name"]]
        rev_class = "is-reversed" if card["pos"] == "逆位" else ""
        badge = "<div class='status-badge rev-badge'>▼ 逆位 Reversed</div>" if card["pos"] == "逆位" else "<div class='status-badge up-badge'>▲ 正位 Upright</div>"
        meaning = data["rev"] if card["pos"] == "逆位" else data["up"]
        p_class = "rev-panel" if card["pos"] == "逆位" else ""
        
        st.markdown(f"""
        <div class="card-slot">
            <div class="tarot-frame {rev_class}">
                <div class="tarot-inner"><div class="tarot-front"><img src="{data['img_url']}"></div></div>
            </div>
            <div class="wiki-panel {p_class}">
                <div class="wiki-title">{card["name"]}</div>
                <div style="text-align: center;">{badge}</div>
                <div class="wiki-row"><span class="wiki-label">元素/占星：</span><span class="wiki-highlight">{data['elem']}</span> / <span style="color:#c084fc; font-weight:bold;">{data['astro']}</span></div>
                <div class="wiki-row"><span class="wiki-label">关键字：</span><span class="wiki-value">{data['tags']}</span></div>
                <div class="wiki-row" style="margin-top:8px;"><span class="wiki-label">解析：</span><span class="wiki-value">{meaning}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.step == step_req_minor - 1:
            if st.button(f"启示 3张辅牌", key=f"btn_min_{stage_name}", use_container_width=True):
                st.session_state.spread[state_key]["minors"] = [draw_card(False) for _ in range(3)]
                st.session_state.step = step_req_minor; st.rerun()
                
        if st.session_state.step >= step_req_minor:
            minors_html = "<div style='display:flex; flex-direction:column; align-items:center; width:100%;'>"
            for m_card in st.session_state.spread[state_key]["minors"]:
                m_data = MINORS[m_card["name"]]
                m_img_transform = "transform: rotate(180deg);" if m_card["pos"] == "逆位" else ""
                m_badge = "<span style='color:#ef4444;'>[逆位]</span>" if m_card["pos"] == "逆位" else "<span style='color:#22c55e;'>[正位]</span>"
                m_meaning = m_data["rev"] if m_card["pos"] == "逆位" else m_data["up"]
                border_color = "#ef4444" if m_card["pos"] == "逆位" else "#6b7280"
                minors_html += f"<div class='minor-card-container' style='border-top-color: {border_color};'><div style='width:100%; display:flex; justify-content:center;'><div class='minor-img-wrapper'><img src='{m_data['img_url']}' style='{m_img_transform}'></div></div><div class='minor-text'><div style='color:#eab308; font-size:14px; font-weight:bold; margin-bottom:8px; text-align:center;'>{m_card['name']} {m_badge}</div><div style='color:#9ca3af; margin-bottom:8px; text-align:center;'>属性: {m_data['elem']} | 关键字: {m_data['tags']}</div><div style='color:#d1d5db; border-top: 1px dashed #4b5563; padding-top: 10px;'>{m_meaning}</div></div></div>"
            minors_html += "</div>"
            st.markdown(minors_html, unsafe_allow_html=True)

# ==========================================
# 5. 仪式流程
# ==========================================
if st.session_state.step == 0:
    st.markdown("""
        <div class="header-box">
            <div class="header-line"></div>
            <div class="header-text">塔罗占卜</div>
            <div class="header-line-rev"></div>
        </div>
        <div class="hero-subtitle">
            跨越维度的意识链接已经就绪。<br>
            请在静默中集中精神，将你内心深处的困惑，铭刻于下方的矩阵之中。
        </div>
    """, unsafe_allow_html=True)
    
    q = st.text_input("", placeholder="例如：我的下一个重大决定会带来什么影响？", label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        if st.button("开始连接命运星轨", use_container_width=True):
            if q: st.session_state.q = q; st.session_state.step = 1; st.rerun()
            else: st.warning("空白无法被解读，请写下你的问题。")

if st.session_state.step > 0:
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align:center; color:#eab308; border-bottom:1px dashed #374151; padding-bottom:15px; margin-bottom:30px;'>当前命题：{st.session_state.q}</h4>", unsafe_allow_html=True)
    
    col_p, col_pr, col_f = st.columns(3)
    with col_p: render_slot("过去起因", 2, 3, "past")
    with col_pr: render_slot("现在状况", 4, 5, "present")
    with col_f: render_slot("未来走向", 6, 7, "future")

# ==========================================
# 6. 大模型综合解盘 (Prompt 强力抗偏见)
# ==========================================
if st.session_state.step == 7:
    st.divider()
    col_ai1, col_ai2, col_ai3 = st.columns([1, 1, 1])
    with col_ai2:
        if st.button("🌌 请求占星师高维解阵", use_container_width=True):
            if not api_key: st.error("请先在应用后台 (Secrets) 中配置 API Key。")
            else:
                try:
                    client = OpenAI(api_key=api_key, base_url=api_base)
                    
                    prompt = f"问卜者的问题是：【{st.session_state.q}】。\n\n"
                    for stage, key in zip(["【过去】", "【现在】", "【未来】"], ["past", "present", "future"]):
                        maj = st.session_state.spread[key]["major"]
                        mins = st.session_state.spread[key]["minors"]
                        mins_str = "、".join([f"{m['name']}({m['pos']})" for m in mins])
                        prompt += f"{stage} 宿命主牌：{maj['name']}({maj['pos']}) | 现实辅牌：{mins_str}\n"
                    
                    # 终极 Prompt：加入防“有毒正能量”护栏
                    prompt += """
                    \n解读要求：
                    1. 【极其重要：拒绝强行安慰】大语言模型通常带有讨好人类的倾向，请你彻底摒弃这种设定。必须根据牌面真实情况（尤其是死神、高塔、恶魔、宝剑牌组、逆位等）直言不讳。如果牌面糟糕，请直接点出危机、阻碍甚至失败的可能性，保持真实占卜的客观、严肃与批判性，绝不要强行往好的方向圆。
                    2. 请使用 Markdown 格式排版，多使用标题(###)、分点(1. 2.)或粗体来区分段落。
                    3. 首段必须针对问卜者的问题给出整体基调的绝对真实洞察（好就是好，坏就是坏）。
                    4. 深入分析各阶段主牌宿命如何与辅牌细节相互影响。
                    5. 最后给出具体、基于现实的行动建议（如果是死局，建议可以是放弃或止损）。
                    """
                    
                    with st.spinner(f"正在建立精神连接..."):
                        res = client.chat.completions.create(
                            model=api_model,
                            messages=[{"role": "system", "content": f"你是一位精通神秘学、客观且犀利的塔罗大师。问卜者的问题是：{st.session_state.q}"}, {"role": "user", "content": prompt}],
                            temperature=0.7
                        )
                        st.success("解析完毕：")
                        
                        st.markdown(f"""
                        <div class="ai-interpretation-container">
                            <div class="ai-content">
                                {res.choices[0].message.content}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e: st.error(f"接口调用失败。错误详情：{e}")
            
    st.markdown("<br>", unsafe_allow_html=True)
    col_r1, col_r2, col_r3 = st.columns([1, 1, 1])
    with col_r2:
        if st.button("↻ 结束本次占卜", use_container_width=True):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()