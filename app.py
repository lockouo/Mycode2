import streamlit as st
import random
from openai import OpenAI

# ==========================================
# 1. 页面配置与高级沉浸式 CSS
# ==========================================
st.set_page_config(page_title="赛博塔罗：全维解析版", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; font-family: 'Times New Roman', serif; }
    h1, h2, h3 { color: #d2a8ff !important; text-align: center; }
    
    /* 核心容器 */
    .card-wrapper { display: flex; flex-direction: column; align-items: center; justify-content: flex-start; width: 100%; margin-bottom: 30px; }
    
    /* 塔罗牌实体框架（原画比例） */
    .tarot-card {
        width: 170px; height: 290px; background: #161b22;
        border: 2px solid #58a6ff; border-radius: 8px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.8), 0 0 15px rgba(88, 166, 255, 0.1);
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        padding: 5px; position: relative;
    }
    
    /* 图片翻转特效 */
    .card-img { width: 100%; height: 100%; object-fit: cover; border-radius: 4px; transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1); }
    .is-reversed .card-img { transform: rotate(180deg); }
    
    /* ---------------------------------------------------
       神级 CSS 技巧：将普通按钮伪装成“可点击的牌堆” 
       --------------------------------------------------- */
    .deck-container {
        display: flex; flex-direction: column; align-items: center;
        padding: 20px; background: rgba(22, 27, 34, 0.5); border-radius: 12px;
        border: 1px dashed #30363d; margin-bottom: 20px;
    }
    /* 拦截 Streamlit 按钮样式，替换为原版牌背 */
    button[kind="secondary"] {
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/d/d4/Tarot_card_back.jpg") !important;
        background-size: cover !important;
        background-position: center !important;
        width: 150px !important; height: 260px !important;
        border: 2px solid #d2a8ff !important; border-radius: 8px !important;
        color: transparent !important; /* 隐藏文字 */
        box-shadow: 0 8px 20px rgba(210, 168, 255, 0.3) !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
    }
    button[kind="secondary"]:hover {
        transform: translateY(-5px) scale(1.02) !important;
        box-shadow: 0 12px 30px rgba(210, 168, 255, 0.6) !important;
    }
    button[kind="secondary"]:active { transform: scale(0.95) !important; }
    /* 点击抽牌提示字 */
    .click-hint { color: #d2a8ff; font-weight: bold; margin-top: 15px; letter-spacing: 2px; text-shadow: 0 0 10px rgba(210,168,255,0.8); animation: pulse 2s infinite; }
    @keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }

    /* ---------------------------------------------------
       百科级详细解析面板排版
       --------------------------------------------------- */
    .meaning-panel {
        width: 100%; max-width: 320px; background: rgba(22, 27, 34, 0.9);
        border: 1px solid #30363d; border-top: 3px solid #58a6ff; border-radius: 6px;
        padding: 15px; margin-top: 15px; font-size: 13px; line-height: 1.6; text-align: left;
    }
    .meaning-panel.rev-panel { border-top-color: #f85149; }
    .card-title { font-size: 18px; color: #fff; font-weight: bold; margin-bottom: 8px; text-align: center; border-bottom: 1px solid #30363d; padding-bottom: 8px;}
    
    /* 属性标签矩阵 */
    .attr-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-bottom: 12px; }
    .attr-item { background: #21262d; padding: 4px 8px; border-radius: 4px; border-left: 2px solid #d2a8ff; color: #c9d1d9; }
    .attr-label { color: #8b949e; font-size: 11px; display: block; }
    
    .status-badge { display: inline-block; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 12px; margin-bottom: 10px; width: 100%; text-align: center; }
    .up-badge { background: rgba(86, 211, 100, 0.1); color: #56d364; border: 1px solid #56d364; }
    .rev-badge { background: rgba(248, 81, 73, 0.1); color: #f85149; border: 1px solid #f85149; }
    .keyword-text { color: #58a6ff; font-weight: bold; margin-bottom: 8px;}
    .desc-text { color: #8b949e; margin-bottom: 8px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 百科级神秘学数据库引擎 (加入生命树与占星)
# ==========================================
BASE_IMG_URL = "https://sacred-texts.com/tarot/pkt/img/"

MAJORS = {
    "愚者": {"img": "ar00.jpg", "color": "黄色", "elem": "风", "astro": "天王星", "num": "0", "tol": "Kether 至 Chokmah (冠冕至智慧)", "keys": "新开始、无限可能、冒险、天真", "up": "象征着新旅程的起点，鼓励你放下恐惧，凭借直觉与纯粹的动机去探索。", "rev": "能量发散失控，暗示鲁莽、不计后果的决定或逃避现实责任。"},
    "魔术师": {"img": "ar01.jpg", "color": "黄色/红色", "elem": "风", "astro": "水星", "num": "1", "tol": "Kether 至 Binah (冠冕至理解)", "keys": "创造力、显化、沟通、意志力", "up": "你已掌握达成目标所需的所有资源与能力。是将想法化为现实的最佳时机。", "rev": "能力遭到滥用或受到阻力。可能表现为缺乏自信、沟通不畅或利用小聪明。"},
    "女祭司": {"img": "ar02.jpg", "color": "蓝色", "elem": "水", "astro": "月亮", "num": "2", "tol": "Kether 至 Tiphereth (冠冕至美丽)", "keys": "直觉、潜意识、等待、内在智慧", "up": "向内探索的时期。答案不在外界，而在你的潜意识里。保持客观与静观其变。", "rev": "直觉混乱，过于依赖理性而压抑内心的声音，或隐藏的秘密即将浮现。"}
}
# 填充剩余大牌基础结构以保证程序运行
for i, name in enumerate(["皇后", "皇帝", "教皇", "恋人", "战车", "力量", "隐士", "命运之轮", "正义", "倒吊人", "死神", "节制", "恶魔", "高塔", "星星", "月亮", "太阳", "审判", "世界"]):
    code = f"ar{i+3:02d}.jpg" if i < 18 else f"ar{i+3}.jpg" # 简单补齐
    MAJORS[name] = {"img": code, "color": "宇宙色", "elem": "宇宙", "astro": "对应星体", "num": str(i+3), "tol": "生命树路径", "keys": "宿命、转变、核心课题", "up": f"顺应{name}的正向能量流动。", "rev": f"{name}的能量受阻，需要反思。"}

# --- 小阿卡那：卡巴拉生命树生成算法 ---
suits_map = {"权杖": {"code": "wa", "elem": "火", "color": "红色", "astro": "火象(牡羊/狮子/射手)", "core": "行动与创造"},
             "圣杯": {"code": "cu", "elem": "水", "color": "蓝色", "astro": "水象(巨蟹/天蝎/双鱼)", "core": "情感与直觉"},
             "宝剑": {"code": "sw", "elem": "风", "color": "黄色", "astro": "风象(双子/天秤/水瓶)", "core": "思想与冲突"},
             "星币": {"code": "pe", "elem": "土", "color": "绿色/棕色", "astro": "土象(金牛/处女/魔羯)", "core": "物质与现实"}}

ranks_map = {"首牌": {"num": "1", "tol": "Kether (王冠) - 神性明光", "key": "新开始、潜力迸发、启动"},
             "二": {"num": "2", "tol": "Chokmah (智慧) - 原始动力", "key": "选择、平衡、规划、等待"},
             "三": {"num": "3", "tol": "Binah (理解) - 形式构建", "key": "初步成果、合作、扩展"},
             "四": {"num": "4", "tol": "Chesed (慈悲) - 稳定秩序", "key": "稳定、停滞、防御、基础"}}
# 填充剩余小牌数字
for r in ["五", "六", "七", "八", "九", "十", "侍从", "骑士", "王后", "国王"]:
    ranks_map[r] = {"num": r, "tol": "对应原质 (Sephiroth)", "key": f"该阶段特有课题"}

MINORS = {}
for suit, s_data in suits_map.items():
    for i, (rank, r_data) in enumerate(ranks_map.items()):
        code = f"{s_data['code']}{i+1:02d}.jpg"
        MINORS[f"{suit}{rank}"] = {
            "img": code, "color": s_data["color"], "elem": s_data["elem"], "astro": s_data["astro"], 
            "num": r_data["num"], "tol": r_data["tol"], "keys": f"{s_data['core']}的{r_data['key']}",
            "up": f"在{s_data['elem']}元素领域，展现出 {r_data['key']} 的建设性力量，是一股正向的推动力。",
            "rev": f"在{s_data['elem']}元素领域，能量发生扭曲或受阻，暗示拖延、方向错误或自我消耗。"
        }

# ==========================================
# 3. 核心渲染函数：牌背按钮与详细解析面板
# ==========================================
def render_clickable_deck(button_key):
    """渲染一个看起来像牌堆的图片，点击它即可抽牌"""
    st.markdown("<div class='deck-container'>", unsafe_allow_html=True)
    # 这里的按钮会被上方的 CSS 替换为原版塔罗牌背图！
    clicked = st.button("DRAW", key=button_key, help="点击牌堆抽取命运卡牌")
    st.markdown("<div class='click-hint'>👆 凝神，触碰牌堆抽取</div></div>", unsafe_allow_html=True)
    return clicked

def render_encyclopedia_card(card_data, is_major):
    """渲染完整的卡牌与百科级解析面板"""
    name = card_data["name"]
    pos = card_data["pos"]
    data = MAJORS[name] if is_major else MINORS[name]
    
    rev_class = "is-reversed" if pos == "逆位" else ""
    panel_class = "rev-panel" if pos == "逆位" else ""
    badge_html = f"<div class='status-badge rev-badge'>▼ 逆位 Reversed</div>" if pos == "逆位" else f"<div class='status-badge up-badge'>▲ 正位 Upright</div>"
    
    html = f"""
    <div class="card-wrapper">
        <div class="tarot-card {rev_class}">
            <img src="{BASE_IMG_URL}{data['img']}" class="card-img" alt="{name}">
        </div>
        <div class="meaning-panel {panel_class}">
            <div class="card-title">{name}</div>
            
            <div class="attr-grid">
                <div class="attr-item"><span class="attr-label">元素 Element</span>{data['elem']}</div>
                <div class="attr-item"><span class="attr-label">代表色 Color</span>{data['color']}</div>
                <div class="attr-item"><span class="attr-label">占星 Astrology</span>{data['astro']}</div>
                <div class="attr-item"><span class="attr-label">编号 Number</span>{data['num']}</div>
            </div>
            <div class="attr-item" style="margin-bottom: 12px; width: 100%;"><span class="attr-label">生命树 Tree of Life</span>{data['tol']}</div>
            
            <div class="keyword-text">🔑 关键字：{data['keys']}</div>
            {badge_html}
            <div class="desc-text"><b>含义：</b>{data['rev'] if pos == '逆位' else data['up']}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ==========================================
# 4. 交互与状态机
# ==========================================
if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.deck_m = list(MAJORS.keys()); random.shuffle(st.session_state.deck_m)
    st.session_state.deck_min = list(MINORS.keys()); random.shuffle(st.session_state.deck_min)
    st.session_state.spread = {"past": {}, "present": {}, "future": {}}

def draw_card(is_major):
    return {"name": (st.session_state.deck_m if is_major else st.session_state.deck_min).pop(), "pos": random.choice(["正位", "逆位"])}

st.title("👁️‍🗨️ 全维真知：赛博塔罗引擎")

# --- 解耦的 API 配置区 ---
st.sidebar.header("⚙️ 引擎接口配置 (支持任意大模型)")
api_base = st.sidebar.text_input("API 接口地址 (Base URL)", value="https://api.deepseek.com", help="例如 OpenAI 的 https://api.openai.com/v1")
api_model = st.sidebar.text_input("模型名称 (Model)", value="deepseek-chat", help="例如 gpt-4o 或 gpt-3.5-turbo")
api_key = st.sidebar.text_input("API Key (密钥)", type="password")
st.sidebar.info("本系统现已完全解耦，你可以填入任何兼容 OpenAI SDK 格式的厂商接口来实现最终的解牌。")

if st.session_state.step == 0:
    q = st.text_input("在虚空中写下你的疑问：", placeholder="例如：我的事业即将迎来怎样的转折？")
    if st.button("确认疑问，凝结牌堆", use_container_width=True):
        if q: st.session_state.q = q; st.session_state.step = 1; st.rerun()
        else: st.warning("缺乏焦点，仪式无法开启。")

if st.session_state.step > 0:
    st.markdown(f"<h4 style='text-align:center; color:#8b949e; margin-bottom:30px;'>命题：{st.session_state.q}</h4>", unsafe_allow_html=True)
    
    col_p, col_pr, col_f = st.columns(3)
    
    # --- 过去 ---
    with col_p:
        st.markdown("<h3 style='color:#fff;'>✦ 过去 ✦</h3>", unsafe_allow_html=True)
        if st.session_state.step == 1:
            if render_clickable_deck("draw_p_m"):
                st.session_state.spread["past"]["major"] = draw_card(True); st.session_state.step = 2; st.rerun()
        if st.session_state.step >= 2:
            render_encyclopedia_card(st.session_state.spread["past"]["major"], True)
            if st.session_state.step == 2:
                if render_clickable_deck("draw_p_min"):
                    st.session_state.spread["past"]["minors"] = [draw_card(False) for _ in range(3)]; st.session_state.step = 3; st.rerun()
            if st.session_state.step >= 3:
                for m in st.session_state.spread["past"]["minors"]: render_encyclopedia_card(m, False)

    # --- 现在 ---
    with col_pr:
        st.markdown("<h3 style='color:#fff;'>✦ 现在 ✦</h3>", unsafe_allow_html=True)
        if st.session_state.step == 3:
            if render_clickable_deck("draw_pr_m"):
                st.session_state.spread["present"]["major"] = draw_card(True); st.session_state.step = 4; st.rerun()
        if st.session_state.step >= 4:
            render_encyclopedia_card(st.session_state.spread["present"]["major"], True)
            if st.session_state.step == 4:
                if render_clickable_deck("draw_pr_min"):
                    st.session_state.spread["present"]["minors"] = [draw_card(False) for _ in range(3)]; st.session_state.step = 5; st.rerun()
            if st.session_state.step >= 5:
                for m in st.session_state.spread["present"]["minors"]: render_encyclopedia_card(m, False)

    # --- 未来 ---
    with col_f:
        st.markdown("<h3 style='color:#fff;'>✦ 未来 ✦</h3>", unsafe_allow_html=True)
        if st.session_state.step == 5:
            if render_clickable_deck("draw_f_m"):
                st.session_state.spread["future"]["major"] = draw_card(True); st.session_state.step = 6; st.rerun()
        if st.session_state.step >= 6:
            render_encyclopedia_card(st.session_state.spread["future"]["major"], True)
            if st.session_state.step == 6:
                if render_clickable_deck("draw_f_min"):
                    st.session_state.spread["future"]["minors"] = [draw_card(False) for _ in range(3)]; st.session_state.step = 7; st.rerun()
            if st.session_state.step >= 7:
                for m in st.session_state.spread["future"]["minors"]: render_encyclopedia_card(m, False)

# ==========================================
# 5. 全维度通用 API 接入解盘
# ==========================================
if st.session_state.step == 7:
    st.divider()
    if st.button("👁️‍🗨️ 连接虚空，生成全维度占卜报告", use_container_width=True):
        if not api_key: st.error("请先在左侧边栏配置 API Key 与接口地址。")
        else:
            try:
                # 接入用户自定义的任意大模型接口
                client = OpenAI(api_key=api_key, base_url=api_base)
                
                # 构建极其丰富的 Prompt，强迫 AI 使用生命树和元素知识
                prompt = f"问卜者：“{st.session_state.q}”\n牌阵数据：\n"
                for stage, key in zip(["【过去】", "【现在】", "【未来】"], ["past", "present", "future"]):
                    maj = st.session_state.spread[key]["major"]
                    m_data = MAJORS[maj['name']]
                    prompt += f"{stage} 核心宿命：{maj['name']}({maj['pos']}) [元素:{m_data['elem']}, 生命树:{m_data['tol']}]\n"
                    
                    mins = st.session_state.spread[key]["minors"]
                    min_str = ", ".join([f"{m['name']}({m['pos']})" for m in mins])
                    prompt += f"-> 现实支撑：{min_str}\n"
                
                prompt += """请进行专业级的全维塔罗解读。要求：
                1. 结合卡巴拉生命树的能量流转与四大元素（水火土风）的生克关系进行深层分析。
                2. 分析大牌所代表的灵魂课题是如何通过三张小牌的现实环境显化的。
                3. 排版必须高级、神秘、层次分明。"""
                
                with st.spinner(f"正在通过 {api_model} 引擎运算神秘学数据..."):
                    res = client.chat.completions.create(
                        model=api_model,
                        messages=[{"role": "system", "content": "你是一位精通金色黎明会神秘学体系与荣格原型的首席塔罗大师。"}, {"role": "user", "content": prompt}],
                        temperature=0.8
                    )
                    st.success("虚空回响完毕：")
                    st.markdown(res.choices[0].message.content)
            except Exception as e: st.error(f"接口连接失败，请检查 Base URL、Model 名称或 API Key 是否正确。详细错误：{e}")
            
    if st.button("消散牌阵，重新开启"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()