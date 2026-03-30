import streamlit as st
import random
from openai import OpenAI

# ==========================================
# 1. 页面配置与原画级 CSS 排版系统
# ==========================================
st.set_page_config(page_title="原画级赛博塔罗", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; font-family: 'Times New Roman', serif; }
    h1, h2, h3 { color: #d2a8ff !important; text-align: center; }
    
    /* 核心容器：绝对居中对齐 */
    .card-wrapper {
        display: flex; flex-direction: column; align-items: center; justify-content: flex-start;
        width: 100%; margin-bottom: 30px;
    }
    
    /* 塔罗牌实体框架（适配原画比例） */
    .tarot-card {
        width: 170px; height: 290px;
        background: #161b22;
        border: 2px solid #58a6ff; border-radius: 8px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.8), 0 0 15px rgba(88, 166, 255, 0.1);
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        padding: 5px; position: relative;
    }
    
    /* 真实图片渲染层与翻转特效 */
    .card-img {
        width: 100%; height: 100%; object-fit: cover; border-radius: 4px;
        transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .is-reversed .card-img { transform: rotate(180deg); }
    
    /* 底部释义面板：精美排版 */
    .meaning-panel {
        width: 100%; max-width: 300px; background: rgba(22, 27, 34, 0.8);
        border: 1px solid #30363d; border-top: 3px solid #58a6ff; border-radius: 6px;
        padding: 15px; margin-top: 15px; font-size: 14px; line-height: 1.6; text-align: left;
    }
    .meaning-panel.rev-panel { border-top-color: #f85149; }
    
    .card-title { font-size: 18px; color: #fff; font-weight: bold; margin-bottom: 8px; text-align: center; border-bottom: 1px solid #30363d; padding-bottom: 8px;}
    .status-badge { display: inline-block; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 12px; margin-bottom: 8px; }
    .up-badge { background: rgba(86, 211, 100, 0.1); color: #56d364; border: 1px solid #56d364; }
    .rev-badge { background: rgba(248, 81, 73, 0.1); color: #f85149; border: 1px solid #f85149; }
    .detail-text { color: #8b949e; }
    .tag-text { color: #d2a8ff; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 原画图库映射引擎 (直连公共档案馆)
# ==========================================
BASE_IMG_URL = "https://sacred-texts.com/tarot/pkt/img/"

# 大阿卡那数据生成 (00 到 21)
majors_list = ["愚者", "魔术师", "女祭司", "皇后", "皇帝", "教皇", "恋人", "战车", "力量", "隐士", "命运之轮", "正义", "倒吊人", "死神", "节制", "恶魔", "高塔", "星星", "月亮", "太阳", "审判", "世界"]
MAJORS = {}
for i, name in enumerate(majors_list):
    code = f"ar{i:02d}" # 生成 ar00, ar01 ... ar21
    MAJORS[name] = {
        "img_url": f"{BASE_IMG_URL}{code}.jpg",
        "up": f"【正位】顺应{name}的原型能量，象征正向的发展与顺畅的宇宙指引。",
        "rev": f"【逆位】{name}的能量受阻或过度，暗示需要反思、调整或面对内心的恐惧。"
    }

# 小阿卡那数据生成 (四个牌组，1 到 14)
suits_map = {"权杖": "wa", "圣杯": "cu", "宝剑": "sw", "星币": "pe"}
ranks_list = ["首牌", "二", "三", "四", "五", "六", "七", "八", "九", "十", "侍从", "骑士", "王后", "国王"]
MINORS = {}
for suit_name, suit_code in suits_map.items():
    for i, rank in enumerate(ranks_list):
        num = i + 1
        code = f"{suit_code}{num:02d}" # 生成 wa01, cu14 等
        MINORS[f"{suit_name}{rank}"] = {
            "img_url": f"{BASE_IMG_URL}{code}.jpg",
            "up": f"【正位】在{suit_name}（{['火','水','风','土'][list(suits_map.keys()).index(suit_name)]}元素）领域，展现出阶次 {rank} 的建设性力量。",
            "rev": f"【逆位】在{suit_name}领域，阶次 {rank} 的能量发生扭曲、延迟或内耗。"
        }

# (注：为了代码精简，此处省略了上百字的详细文案，重点展示图像拉取与排版架构。实际应用中可无缝接入你之前的长篇文案库)

# ==========================================
# 3. 核心渲染函数：图片与排版的完美结合
# ==========================================
def render_real_card(card_data, is_major):
    name = card_data["name"]
    pos = card_data["pos"]
    data = MAJORS[name] if is_major else MINORS[name]
    
    # CSS 控制图片翻转
    rev_class = "is-reversed" if pos == "逆位" else ""
    badge_html = f"<div class='status-badge rev-badge'>▼ 逆位 Reversed</div>" if pos == "逆位" else f"<div class='status-badge up-badge'>▲ 正位 Upright</div>"
    panel_class = "rev-panel" if pos == "逆位" else ""
    meaning = data["rev"] if pos == "逆位" else data["up"]
    
    # 渲染 HTML：完全居中，图片物理翻转，文字绝对端正
    html = f"""
    <div class="card-wrapper">
        <div class="tarot-card {rev_class}">
            <img src="{data['img_url']}" class="card-img" alt="{name}">
        </div>
        <div class="meaning-panel {panel_class}">
            <div class="card-title">{name}</div>
            <div style="text-align: center;">{badge_html}</div>
            <div class="detail-text"><span class="tag-text">💡 释义：</span>{meaning}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ==========================================
# 4. 状态机与仪式交互流程
# ==========================================
if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.deck_m = list(MAJORS.keys()); random.shuffle(st.session_state.deck_m)
    st.session_state.deck_min = list(MINORS.keys()); random.shuffle(st.session_state.deck_min)
    st.session_state.spread = {"past": {}, "present": {}, "future": {}}

def draw_card(is_major):
    return {"name": (st.session_state.deck_m if is_major else st.session_state.deck_min).pop(), "pos": random.choice(["正位", "逆位"])}

st.title("👁️‍🗨️ 原画级 AI 塔罗牌阵")
api_key = st.sidebar.text_input("DeepSeek API Key (解牌必备)", type="password")
st.sidebar.info("已直连 Sacred Texts 档案馆，实时加载 1909 年韦特塔罗原画。逆位时图像将产生真实物理翻转。")

if st.session_state.step == 0:
    q = st.text_input("请在心中默念问题并写下：", placeholder="例如：我的事业转型期应该注意什么？")
    if st.button("开始洗牌仪式", use_container_width=True):
        if q: st.session_state.q = q; st.session_state.step = 1; st.rerun()
        else: st.warning("请输入问题。")

if st.session_state.step > 0:
    st.markdown(f"<h4 style='text-align:center; color:#8b949e; margin-bottom:30px;'>问题：{st.session_state.q}</h4>", unsafe_allow_html=True)
    
    col_p, col_pr, col_f = st.columns(3)
    
    # --- 过去 ---
    with col_p:
        st.markdown("<h3 style='color:#fff;'>✦ 过去 ✦</h3>", unsafe_allow_html=True)
        if st.session_state.step == 1:
            if st.button("揭露过去 (大牌)"): st.session_state.spread["past"]["major"] = draw_card(True); st.session_state.step = 2; st.rerun()
        if st.session_state.step >= 2:
            render_real_card(st.session_state.spread["past"]["major"], True)
            if st.session_state.step == 2:
                if st.button("抽 3 张小牌 (细节)"): st.session_state.spread["past"]["minors"] = [draw_card(False) for _ in range(3)]; st.session_state.step = 3; st.rerun()
            if st.session_state.step >= 3:
                for m in st.session_state.spread["past"]["minors"]: render_real_card(m, False)

    # --- 现在 ---
    with col_pr:
        st.markdown("<h3 style='color:#fff;'>✦ 现在 ✦</h3>", unsafe_allow_html=True)
        if st.session_state.step == 3:
            if st.button("揭露现在 (大牌)"): st.session_state.spread["present"]["major"] = draw_card(True); st.session_state.step = 4; st.rerun()
        if st.session_state.step >= 4:
            render_real_card(st.session_state.spread["present"]["major"], True)
            if st.session_state.step == 4:
                if st.button("抽 3 张小牌 (细节)"): st.session_state.spread["present"]["minors"] = [draw_card(False) for _ in range(3)]; st.session_state.step = 5; st.rerun()
            if st.session_state.step >= 5:
                for m in st.session_state.spread["present"]["minors"]: render_real_card(m, False)

    # --- 未来 ---
    with col_f:
        st.markdown("<h3 style='color:#fff;'>✦ 未来 ✦</h3>", unsafe_allow_html=True)
        if st.session_state.step == 5:
            if st.button("揭露未来 (大牌)"): st.session_state.spread["future"]["major"] = draw_card(True); st.session_state.step = 6; st.rerun()
        if st.session_state.step >= 6:
            render_real_card(st.session_state.spread["future"]["major"], True)
            if st.session_state.step == 6:
                if st.button("抽 3 张小牌 (细节)"): st.session_state.spread["future"]["minors"] = [draw_card(False) for _ in range(3)]; st.session_state.step = 7; st.rerun()
            if st.session_state.step >= 7:
                for m in st.session_state.spread["future"]["minors"]: render_real_card(m, False)

# ==========================================
# 5. 图像结合的 AI 深度解读
# ==========================================
if st.session_state.step == 7:
    st.divider()
    if st.button("👁️‍🗨️ 牌阵已成，请求 DeepSeek 结合图像全盘解阵", use_container_width=True):
        if not api_key: st.error("请在左侧边栏配置 API Key。")
        else:
            try:
                client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
                prompt = f"问卜者：“{st.session_state.q}”\n牌阵数据：\n"
                for stage, key in zip(["【过去】", "【现在】", "【未来】"], ["past", "present", "future"]):
                    maj = st.session_state.spread[key]["major"]
                    mins = st.session_state.spread[key]["minors"]
                    prompt += f"{stage} 宿命大牌：{maj['name']}({maj['pos']}) | 现实途径小牌：{', '.join([f'{m['name']}({m['pos']})' for m in mins])}\n"
                
                prompt += """请进行顶级塔罗解读。要求：必须结合这 12 张牌在韦特塔罗牌中的【原画图像细节】（例如人物动作、颜色、背景元素）进行深度分析。大牌说明宿命，小牌说明现实途径。排版清晰。"""
                
                with st.spinner("正在提取原画星象信息与图腾能量..."):
                    res = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是一位专注于韦特塔罗图像符号学的解牌大师。"}, {"role": "user", "content": prompt}],
                        temperature=0.8
                    )
                    st.success("解析完毕：")
                    st.markdown(res.choices[0].message.content)
            except Exception as e: st.error(f"连接失败：{e}")
            
    if st.button("开启新一轮占卜"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()