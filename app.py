import streamlit as st
import random
from openai import OpenAI

# ==========================================
# 1. 页面配置与典籍级 CSS 排版系统
# ==========================================
st.set_page_config(page_title="原画级赛博塔罗 - 终极版", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background-color: #080a0f; color: #c9d1d9; font-family: 'Times New Roman', serif; }
    h1, h2, h3 { color: #d2a8ff !important; text-align: center; font-weight: 300; letter-spacing: 2px;}
    
    /* 虚拟牌堆与抽卡特效 */
    .deck-container {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        margin: 40px 0;
    }
    .card-back {
        width: 150px; height: 260px;
        background: radial-gradient(circle at center, #2a1a4a 0%, #0a0514 100%);
        border: 2px solid #58a6ff; border-radius: 8px;
        box-shadow: 0 0 20px rgba(88, 166, 255, 0.4), inset 0 0 15px rgba(210, 168, 255, 0.3);
        background-image: repeating-linear-gradient(45deg, rgba(88,166,255,0.1) 0px, rgba(88,166,255,0.1) 2px, transparent 2px, transparent 8px);
        animation: breath 3s infinite ease-in-out;
        margin-bottom: 15px; position: relative;
    }
    .card-back::after {
        content: '✡'; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
        font-size: 50px; color: rgba(210, 168, 255, 0.6);
    }
    @keyframes breath {
        0% { box-shadow: 0 0 20px rgba(88, 166, 255, 0.2); transform: translateY(0px); }
        50% { box-shadow: 0 0 40px rgba(210, 168, 255, 0.6); transform: translateY(-5px); }
        100% { box-shadow: 0 0 20px rgba(88, 166, 255, 0.2); transform: translateY(0px); }
    }

    /* 卡牌正面的展示框 */
    .card-wrapper { display: flex; flex-direction: column; align-items: center; margin-bottom: 30px; }
    .tarot-card {
        width: 160px; height: 275px; background: #161b22; border: 1px solid #58a6ff; border-radius: 6px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.8); padding: 4px;
    }
    .card-img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.6s; }
    .is-reversed .card-img { transform: rotate(180deg); }
    
    /* 典籍级数据面板排版 */
    .grimoire-panel {
        width: 100%; background: linear-gradient(180deg, rgba(22, 27, 34, 0.9) 0%, rgba(13, 17, 23, 0.9) 100%);
        border: 1px solid #30363d; border-top: 3px solid #58a6ff; border-radius: 6px;
        padding: 15px; margin-top: 15px; font-size: 13px; line-height: 1.6;
    }
    .grimoire-panel.rev-panel { border-top-color: #f85149; }
    .card-title { font-size: 18px; color: #fff; font-weight: bold; text-align: center; margin-bottom: 10px; }
    
    .data-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px dashed #444; }
    .data-item { background: rgba(0,0,0,0.3); padding: 4px 8px; border-radius: 4px; color: #8b949e;}
    .data-val { color: #d2a8ff; font-weight: bold; float: right;}
    
    .keyword-box { color: #58a6ff; margin-bottom: 10px; font-weight: bold; text-align: center; }
    .meaning-text { color: #c9d1d9; text-align: justify; }
    .pos-badge { text-align: center; font-weight: bold; margin-bottom: 10px; font-size: 14px;}
    .pos-up { color: #56d364; } .pos-rev { color: #f85149; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 典籍级塔罗数据库 (融合你提供的高阶数据结构)
# ==========================================
BASE_IMG_URL = "https://sacred-texts.com/tarot/pkt/img/"

# 以【权杖首牌】和【愚者】为例，展示高阶数据结构。
# 实际商业项目中，你可以按照这个 Schema 填满所有 78 张牌的数据。
TAROT_DB = {
    # ------ 小阿卡那示例 ------
    "权杖首牌 (Ace Of Wands)": {
        "img": f"{BASE_IMG_URL}wa01.jpg",
        "color": "红色",
        "element": "火",
        "astro": "牡羊、狮子、射手",
        "number": "1",
        "kabbalah": "Kether (王冠)",
        "keywords": "新行动、创造、机会、灵感、启动",
        "up": "【正位】象征着新的开始、创造力、激情与行动力的迸发。代表一个充满潜力的新机会或项目的启动，鼓励积极行动、勇敢探索神性启示下的新开端。",
        "rev": "【逆位】反映能量失控导致的拖延、方向错误或自我否定。表现为热情消退、计划缺失及资源浪费，需重新审视目标与动机。"
    },
    # ------ 大阿卡那示例 ------
    "愚者 (The Fool)": {
        "img": f"{BASE_IMG_URL}ar00.jpg",
        "color": "黄色 (代表风与智力)",
        "element": "风",
        "astro": "天王星",
        "number": "0",
        "kabbalah": "Kether 与 Chokmah 之间",
        "keywords": "无限潜能、流浪、纯真、冒险、信仰之跃",
        "up": "【正位】代表着无限的潜能与新的冒险。此时你应该听从内心的直觉，放下对未知的恐惧，像孩子般纯粹地投入新事物，不计后果地追求精神自由。",
        "rev": "【逆位】能量过度发散导致鲁莽与冲动。暗示计划不周、逃避现实责任，在悬崖边失足跌落，需要警惕盲目乐观与不切实际的幻想。"
    }
}

# (系统补全逻辑：为了保证代码能抽满78张牌，未手动录入的牌将由算法生成默认结构)
majors_names = ["魔术师", "女祭司", "皇后", "皇帝", "教皇", "恋人", "战车", "力量", "隐士", "命运之轮", "正义", "倒吊人", "死神", "节制", "恶魔", "高塔", "星星", "月亮", "太阳", "审判", "世界"]
for i, n in enumerate(majors_names):
    TAROT_DB[f"{n} (Major)"] = {"img": f"{BASE_IMG_URL}ar{i+1:02d}.jpg", "color": "秘仪原色", "element": "以太", "astro": "宇宙星象", "number": str(i+1), "kabbalah": "生命树路径", "keywords": "宿命、转变、神性指引", "up": f"【正位】顺应{n}的宇宙能量，迎来正向的业力发展。", "rev": f"【逆位】{n}的能量受阻，暗示内在恐惧或外界障碍。"}

suits = {"权杖": "wa", "圣杯": "cu", "宝剑": "sw", "星币": "pe"}
ranks = ["二", "三", "四", "五", "六", "七", "八", "九", "十", "侍从", "骑士", "王后", "国王"]
for s_name, s_code in suits.items():
    for i, r in enumerate(ranks):
        TAROT_DB[f"{s_name}{r} (Minor)"] = {"img": f"{BASE_IMG_URL}{s_code}{i+2:02d}.jpg", "color": "元素主色", "element": s_name, "astro": "对应星座区间", "number": str(i+2), "kabbalah": "源质映射", "keywords": "现实发展、情绪起伏", "up": f"【正位】{s_name}的能量得到良性发展。", "rev": f"【逆位】{s_name}的能量发生扭曲或匮乏。"}


# ==========================================
# 3. 核心渲染组件
# ==========================================
def render_grimoire_card(card_data):
    name = card_data["name"]
    pos = card_data["pos"]
    data = TAROT_DB[name]
    
    rev_class = "is-reversed" if pos == "逆位" else ""
    panel_class = "rev-panel" if pos == "逆位" else ""
    pos_html = "<div class='pos-badge pos-rev'>▼ 逆位 Reversed</div>" if pos == "逆位" else "<div class='pos-badge pos-up'>▲ 正位 Upright</div>"
    meaning = data["rev"] if pos == "逆位" else data["up"]
    
    html = f"""
    <div class="card-wrapper">
        <div class="tarot-card {rev_class}"><img src="{data['img']}" class="card-img"></div>
        <div class="grimoire-panel {panel_class}">
            <div class="card-title">{name}</div>
            {pos_html}
            <div class="keyword-box">✦ {data['keywords']} ✦</div>
            <div class="data-grid">
                <div class="data-item">元素<span class="data-val">{data['element']}</span></div>
                <div class="data-item">代表色<span class="data-val">{data['color']}</span></div>
                <div class="data-item">占星连结<span class="data-val">{data['astro']}</span></div>
                <div class="data-item">数字编号<span class="data-val">{data['number']}</span></div>
                <div class="data-item" style="grid-column: span 2;">生命树<span class="data-val">{data['kabbalah']}</span></div>
            </div>
            <div class="meaning-text">{meaning}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_deck_interaction(button_text, action_key):
    """渲染虚拟牌堆及隐形交互按钮"""
    st.markdown("""
    <div class="deck-container">
        <div class="card-back"></div>
        <p style="color:#888; font-size:12px; margin-top:5px;">凝视牌背，感受能量</p>
    </div>
    """, unsafe_allow_html=True)
    return st.button(button_text, key=action_key, use_container_width=True)

# ==========================================
# 4. 交互状态与灵界配置
# ==========================================
if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.deck = list(TAROT_DB.keys()); random.shuffle(st.session_state.deck)
    st.session_state.spread = {"past": [], "present": [], "future": []}

def draw_card():
    return {"name": st.session_state.deck.pop(), "pos": random.choice(["正位", "逆位"])}

st.title("👁️‍🗨️ 阿卡夏塔罗：全息典籍版")

# 【优化 1：完全解耦的大模型 API 配置】
st.sidebar.header("🔑 大模型节点接入")
st.sidebar.info("本系统兼容任意基于 OpenAI 格式的 API（如 DeepSeek, 通义千问, Kimi, GPT-4 等）。")
api_base = st.sidebar.text_input("API Base URL", value="https://api.deepseek.com", help="例如：https://api.openai.com/v1 或其他厂商接口")
api_model = st.sidebar.text_input("模型名称 (Model)", value="deepseek-chat", help="例如：gpt-4o, qwen-max 等")
api_key = st.sidebar.text_input("API Key", type="password")

if st.session_state.step == 0:
    q = st.text_input("在心中默念困惑，将意念注入于此：")
    if st.button("构建魔法阵", use_container_width=True):
        if q: st.session_state.q = q; st.session_state.step = 1; st.rerun()

if st.session_state.step > 0:
    st.markdown(f"<h4 style='text-align:center; color:#8b949e; margin-bottom:10px;'>命题：{st.session_state.q}</h4>", unsafe_allow_html=True)
    
    # 牌阵展示区
    col_p, col_pr, col_f = st.columns(3)
    
    with col_p:
        st.markdown("<h3 style='color:#fff;'>✦ 过去 ✦</h3>", unsafe_allow_html=True)
        if st.session_state.step == 1:
            # 【优化 2：视觉牌堆交互】
            if render_deck_interaction("👆 从牌堆抽取【过去】能量", "btn_p"):
                st.session_state.spread["past"].append(draw_card()); st.session_state.step = 2; st.rerun()
        if st.session_state.step >= 2:
            for c in st.session_state.spread["past"]: render_grimoire_card(c)

    with col_pr:
        st.markdown("<h3 style='color:#fff;'>✦ 现在 ✦</h3>", unsafe_allow_html=True)
        if st.session_state.step == 2:
            if render_deck_interaction("👆 从牌堆抽取【现在】能量", "btn_pr"):
                st.session_state.spread["present"].append(draw_card()); st.session_state.step = 3; st.rerun()
        if st.session_state.step >= 3:
            for c in st.session_state.spread["present"]: render_grimoire_card(c)

    with col_f:
        st.markdown("<h3 style='color:#fff;'>✦ 未来 ✦</h3>", unsafe_allow_html=True)
        if st.session_state.step == 3:
            if render_deck_interaction("👆 从牌堆抽取【未来】能量", "btn_f"):
                st.session_state.spread["future"].append(draw_card()); st.session_state.step = 4; st.rerun()
        if st.session_state.step >= 4:
            for c in st.session_state.spread["future"]: render_grimoire_card(c)

# ==========================================
# 5. AI 综合解盘
# ==========================================
if st.session_state.step == 4:
    st.divider()
    if st.button("👁️‍🗨️ 连接大模型，基于典籍数据进行高维解阵", use_container_width=True):
        if not api_key: st.error("错误：请先在左侧边栏配置 API 节点信息。")
        else:
            try:
                # 使用用户自定义的 API 参数
                client = OpenAI(api_key=api_key, base_url=api_base)
                
                # 构建极其详尽的包含神秘学要素的 Prompt
                prompt = f"问卜者问题：“{st.session_state.q}”\n牌阵数据：\n"
                for stage, key in zip(["【过去】", "【现在】", "【未来】"], ["past", "present", "future"]):
                    card = st.session_state.spread[key][0]
                    c_data = TAROT_DB[card['name']]
                    prompt += f"{stage}: {card['name']}({card['pos']}) | 元素:{c_data['element']} | 占星:{c_data['astro']} | 生命树:{c_data['kabbalah']}\n"
                
                prompt += """请结合上述提供的元素、占星与卡巴拉生命树信息，进行最顶级的专业塔罗解读。分析这三张牌在神秘学能量上的流转与冲突，并给出清晰的行动指引。"""
                
                with st.spinner("大模型正在跨维度提取能量，撰写解盘报告..."):
                    res = client.chat.completions.create(
                        model=api_model,
                        messages=[{"role": "system", "content": "你是一位顶级神秘学塔罗大师。"}, {"role": "user", "content": prompt}],
                        temperature=0.7
                    )
                    st.success("高维解析完毕：")
                    st.markdown(res.choices[0].message.content)
            except Exception as e: st.error(f"模型节点连接失败，请检查配置：{e}")
            
    if st.button("重置星轨，开启新一局"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()