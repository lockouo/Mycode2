import streamlit as st
import random
import hashlib
from openai import OpenAI

# ==========================================
# 1. 页面配置与绝对对齐的 CSS 布局系统
# ==========================================
st.set_page_config(page_title="赛博塔罗：几何真理版", layout="wide", initial_sidebar_state="collapsed")

# 解决所有排版歪斜问题，使用强约束的 Flexbox 和 Grid
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Times New Roman', serif; }
    
    /* 核心卡牌容器：绝对居中，杜绝歪斜 */
    .card-wrapper {
        display: flex; flex-direction: column; align-items: center; justify-content: flex-start;
        width: 100%; margin-bottom: 2rem;
    }
    
    /* 塔罗牌实体框架 */
    .tarot-card {
        width: 180px; height: 300px;
        background: linear-gradient(135deg, #111 0%, #050505 100%);
        border: 2px solid #b8860b; border-radius: 12px;
        box-shadow: 0 10px 30px rgba(184, 134, 11, 0.15), inset 0 0 20px rgba(184, 134, 11, 0.1);
        display: flex; flex-direction: column; justify-content: space-between; align-items: center;
        padding: 15px 10px; position: relative; overflow: hidden;
    }
    
    /* 四角的神秘学装饰点 */
    .tarot-card::before, .tarot-card::after {
        content: ''; position: absolute; width: 6px; height: 6px; background: #b8860b; border-radius: 50%;
    }
    .tarot-card::before { top: 8px; left: 8px; box-shadow: 156px 0 0 #b8860b; }
    .tarot-card::after { bottom: 8px; left: 8px; box-shadow: 156px 0 0 #b8860b; }

    /* SVG 矢量图形画板：独立翻转 */
    .svg-container {
        width: 140px; height: 200px; display: flex; justify-content: center; align-items: center;
        transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .is-reversed .svg-container { transform: rotate(180deg); filter: hue-rotate(180deg); }
    
    /* 文本排版 */
    .card-header { font-size: 12px; color: #888; letter-spacing: 2px; text-transform: uppercase; z-index: 2; }
    .card-title { font-size: 18px; color: #b8860b; font-weight: bold; text-align: center; z-index: 2; border-top: 1px solid rgba(184, 134, 11, 0.3); padding-top: 8px; width: 80%;}
    
    /* 释义面板：等宽、对齐、高级感 */
    .meaning-panel {
        width: 100%; max-width: 320px; background: rgba(20, 20, 20, 0.8);
        border: 1px solid #333; border-top: 3px solid #b8860b; border-radius: 6px;
        padding: 15px; margin-top: 15px; font-size: 14px; line-height: 1.6; text-align: left;
    }
    .meaning-panel.rev-panel { border-top-color: #8b0000; }
    .status-badge { display: inline-block; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; margin-bottom: 10px; }
    .up-badge { background: rgba(184, 134, 11, 0.2); color: #b8860b; border: 1px solid #b8860b; }
    .rev-badge { background: rgba(139, 0, 0, 0.2); color: #ff4c4c; border: 1px solid #8b0000; }
    .detail-text { color: #ccc; margin-top: 8px; }
    .section-title { color: #fff; font-size: 13px; font-weight: bold; margin-top: 12px; margin-bottom: 4px; border-bottom: 1px dashed #444; padding-bottom: 4px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 独家技术：程序化 SVG 几何牌面生成器
# ==========================================
def generate_svg_art(card_name):
    """
    根据卡牌名称的哈希值，利用纯代码数学算法生成独一无二的几何神秘学阵法。
    这样无需任何外部图片，就能画出极其精美、充满科技感与神秘感的牌面。
    """
    # 提取稳定的哈希值作为绘图种子
    seed = int(hashlib.md5(card_name.encode('utf-8')).hexdigest(), 16)
    
    svg_elements = []
    # 基础法阵圆环
    svg_elements.append(f'<circle cx="50" cy="50" r="45" stroke="#b8860b" stroke-width="1" fill="none" opacity="0.5"/>')
    svg_elements.append(f'<circle cx="50" cy="50" r="{30 + (seed%10)}" stroke="#b8860b" stroke-width="0.5" fill="none" stroke-dasharray="2,2"/>')
    
    # 动态生成内切多边形或星芒
    points = 3 + (seed % 6) # 3到8边形
    angle_step = 360 / points
    path_data = ""
    for i in range(points):
        import math
        angle = math.radians(i * angle_step + (seed % 90))
        r = 40
        x = 50 + r * math.cos(angle)
        y = 50 + r * math.sin(angle)
        if i == 0: path_data += f"M {x} {y} "
        else: path_data += f"L {x} {y} "
    path_data += "Z"
    svg_elements.append(f'<path d="{path_data}" stroke="#d4af37" stroke-width="1.5" fill="rgba(184, 134, 11, {0.05 + (seed%10)*0.01})"/>')
    
    # 中心核心图腾（根据花色或大牌特征变换）
    if "权杖" in card_name or "Fool" in card_name:
        svg_elements.append('<line x1="50" y1="20" x2="50" y2="80" stroke="#ff8c00" stroke-width="3"/>')
        svg_elements.append('<circle cx="50" cy="20" r="4" fill="#ff8c00"/>')
    elif "圣杯" in card_name or "Moon" in card_name:
        svg_elements.append('<path d="M30,40 Q50,80 70,40 Z" fill="none" stroke="#4169e1" stroke-width="2"/>')
        svg_elements.append('<path d="M40,40 Q50,50 60,40" fill="none" stroke="#4169e1" stroke-width="2"/>')
    elif "宝剑" in card_name or "Justice" in card_name:
        svg_elements.append('<polygon points="48,15 52,15 50,85" fill="#c0c0c0"/>')
        svg_elements.append('<line x1="35" y1="30" x2="65" y2="30" stroke="#c0c0c0" stroke-width="3"/>')
    elif "星币" in card_name or "Sun" in card_name:
        svg_elements.append('<circle cx="50" cy="50" r="15" fill="none" stroke="#ffd700" stroke-width="3"/>')
        svg_elements.append('<circle cx="50" cy="50" r="5" fill="#ffd700"/>')
    else:
        # 通用大神秘学符号：全视之眼或六芒星变体
        svg_elements.append('<path d="M20,50 Q50,20 80,50 Q50,80 20,50 Z" fill="none" stroke="#d4af37" stroke-width="2"/>')
        svg_elements.append(f'<circle cx="50" cy="50" r="{10 + (seed%8)}" fill="rgba(212, 175, 55, 0.5)"/>')

    svg_content = "".join(svg_elements)
    return f'<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%; filter: drop-shadow(0 0 8px rgba(184,134,11,0.6));">{svg_content}</svg>'

# ==========================================
# 3. 塔罗数据引擎 (保持上一版的深度)
# ==========================================
# (为了代码精简，这里保留核心架构，实际运行时你可自行扩充文案)
MAJORS = {
    "愚者 (The Fool)": {"tags": "开端, 冒险, 盲目", "up": "代表无限的潜能与新的冒险。放下对未知的恐惧，听从直觉。", "rev": "能量过度发散导致鲁莽与冲动。暗示计划不周、逃避现实责任。"},
    "魔术师 (The Magician)": {"tags": "创造, 沟通, 显化", "up": "将潜能转化为现实的极佳时机。你掌握着解决问题的资源。", "rev": "能力遭到滥用或受到阻碍。缺乏自信、沟通不畅。"},
    "女祭司 (The High Priestess)": {"tags": "直觉, 潜意识, 等待", "up": "向内探索的时期。答案在你的潜意识里。保持客观与中立。", "rev": "直觉混乱或被忽视。过于依赖理性而压抑内心。"}
}
for name in ["皇后", "皇帝", "教皇", "恋人", "战车", "力量", "隐士", "命运之轮", "正义", "倒吊人", "死神", "节制", "恶魔", "高塔", "星星", "月亮", "太阳", "审判", "世界"]:
    MAJORS[name] = {"tags": "命运, 转变", "up": f"顺应宇宙能量流动，{name}带来正向指引。", "rev": f"能量受阻，{name}提醒你需要深刻的反思。"}

MINORS = {}
suits = {"权杖": "火/行动", "圣杯": "水/情感", "宝剑": "风/思想", "星币": "土/物质"}
ranks = {"首牌": "开端与迸发", "二": "选择与平衡", "三": "合作与成长"}
for r_name in ["四", "五", "六", "七", "八", "九", "十", "侍从", "骑士", "王后", "国王"]: ranks[r_name] = "该阶段的特定挑战与发展"
for suit, elem in suits.items():
    for rank, core in ranks.items():
        MINORS[f"{suit}{rank}"] = {
            "tags": f"{elem}的{core}",
            "up": f"在{elem}层面，展现出正向的{core}能量。顺势而为。",
            "rev": f"在{elem}层面遭遇阻碍。{core}的能量发生扭曲，需调整。"
        }

# ==========================================
# 4. 状态机与渲染逻辑
# ==========================================
if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.deck_m = list(MAJORS.keys()); random.shuffle(st.session_state.deck_m)
    st.session_state.deck_min = list(MINORS.keys()); random.shuffle(st.session_state.deck_min)
    st.session_state.spread = {"past": {}, "present": {}, "future": {}}

def draw_card(is_major):
    return {"name": (st.session_state.deck_m if is_major else st.session_state.deck_min).pop(), 
            "pos": random.choice(["正位", "逆位"])}

def render_ui_card(card_data, is_major):
    name = card_data["name"]
    pos = card_data["pos"]
    data = MAJORS[name] if is_major else MINORS[name]
    
    rev_class = "is-reversed" if pos == "逆位" else ""
    badge_html = f"<div class='status-badge rev-badge'>▼ 逆位 Reversed</div>" if pos == "逆位" else f"<div class='status-badge up-badge'>▲ 正位 Upright</div>"
    panel_class = "rev-panel" if pos == "逆位" else ""
    meaning = data["rev"] if pos == "逆位" else data["up"]
    c_type = "MAJOR ARCANA" if is_major else "MINOR ARCANA"
    
    # 核心：将 SVG 图形嵌入 HTML，保证 100% 对齐和独立翻转
    svg_art = generate_svg_art(name)
    
    html = f"""
    <div class="card-wrapper">
        <div class="tarot-card {rev_class}">
            <div class="card-header">{c_type}</div>
            <div class="svg-container">{svg_art}</div>
            <div class="card-title">{name}</div>
        </div>
        <div class="meaning-panel {panel_class}">
            {badge_html}
            <div class="section-title">核心枢纽</div>
            <div class="detail-text" style="color:#b8860b;">{data['tags']}</div>
            <div class="section-title">启示录</div>
            <div class="detail-text">{meaning}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ==========================================
# 5. 主界面交互流程
# ==========================================
st.title("🌌 AI 量子塔罗：几何真理阵列")
api_key = st.sidebar.text_input("DeepSeek API Key (解读全阵必备)", type="password")
st.sidebar.info("本应用采用纯代码几何演算绘制牌面，确保每一帧的对齐与神秘学美感。")

if st.session_state.step == 0:
    q = st.text_input("在心中构建你的疑问，将其铭刻于此：", placeholder="例如：我近期的财务状况会有何突破？")
    if st.button("封存疑问，开启洗牌仪式", use_container_width=True):
        if not q: st.warning("空白无法被解读。")
        else:
            st.session_state.q = q
            st.session_state.step = 1; st.rerun()

if st.session_state.step > 0:
    st.markdown(f"<div style='text-align:center; color:#888; margin-bottom: 20px;'>命题：{st.session_state.q}</div>", unsafe_allow_html=True)
    
    col_p, col_pr, col_f = st.columns(3)
    
    # 过去
    with col_p:
        st.markdown("<h3 style='color:#fff;'>✦ 过去 ✦</h3>", unsafe_allow_html=True)
        if st.session_state.step == 1:
            if st.button("唤醒过去的大阿卡那"):
                st.session_state.spread["past"]["major"] = draw_card(True)
                st.session_state.step = 2; st.rerun()
        if st.session_state.step >= 2:
            render_ui_card(st.session_state.spread["past"]["major"], True)
            if st.session_state.step == 2:
                if st.button("揭露过去的 3 个现实印记"):
                    st.session_state.spread["past"]["minors"] = [draw_card(False) for _ in range(3)]
                    st.session_state.step = 3; st.rerun()
            if st.session_state.step >= 3:
                for m in st.session_state.spread["past"]["minors"]: render_ui_card(m, False)

    # 现在
    with col_pr:
        st.markdown("<h3 style='color:#fff;'>✦ 现在 ✦</h3>", unsafe_allow_html=True)
        if st.session_state.step == 3:
            if st.button("唤醒现在的大阿卡那"):
                st.session_state.spread["present"]["major"] = draw_card(True)
                st.session_state.step = 4; st.rerun()
        if st.session_state.step >= 4:
            render_ui_card(st.session_state.spread["present"]["major"], True)
            if st.session_state.step == 4:
                if st.button("揭露现在的 3 个现实印记"):
                    st.session_state.spread["present"]["minors"] = [draw_card(False) for _ in range(3)]
                    st.session_state.step = 5; st.rerun()
            if st.session_state.step >= 5:
                for m in st.session_state.spread["present"]["minors"]: render_ui_card(m, False)

    # 未来
    with col_f:
        st.markdown("<h3 style='color:#fff;'>✦ 未来 ✦</h3>", unsafe_allow_html=True)
        if st.session_state.step == 5:
            if st.button("唤醒未来的大阿卡那"):
                st.session_state.spread["future"]["major"] = draw_card(True)
                st.session_state.step = 6; st.rerun()
        if st.session_state.step >= 6:
            render_ui_card(st.session_state.spread["future"]["major"], True)
            if st.session_state.step == 6:
                if st.button("揭露未来的 3 个现实印记"):
                    st.session_state.spread["future"]["minors"] = [draw_card(False) for _ in range(3)]
                    st.session_state.step = 7; st.rerun()
            if st.session_state.step >= 7:
                for m in st.session_state.spread["future"]["minors"]: render_ui_card(m, False)

# ==========================================
# 6. AI 综合解盘
# ==========================================
if st.session_state.step == 7:
    st.divider()
    if st.button("👁️‍🗨️ 阵列已满，请求 DeepSeek 大师解阵", use_container_width=True):
        if not api_key: st.error("缺乏 API Key，无法连接星界网络。")
        else:
            try:
                client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
                prompt = f"问卜者：“{st.session_state.q}”\n"
                for stage, key in zip(["【过去】", "【现在】", "【未来】"], ["past", "present", "future"]):
                    maj = st.session_state.spread[key]["major"]
                    mins = st.session_state.spread[key]["minors"]
                    prompt += f"{stage} 宿命：{maj['name']}({maj['pos']}) | 现实印记：{', '.join([f'{m['name']}({m['pos']})' for m in mins])}\n"
                
                prompt += "请作为资深塔罗大师进行专业解读。说明大牌的宿命感如何被三张小牌的现实细节所支撑或阻碍。给出深刻的洞察和行动建议。"
                
                with st.spinner("正在接收高维解析..."):
                    res = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是一位顶级塔罗解读师。"}, {"role": "user", "content": prompt}],
                        temperature=0.8
                    )
                    st.success("解析完毕：")
                    st.markdown(res.choices[0].message.content)
            except Exception as e: st.error(f"连接失败：{e}")
            
    if st.button("重置星轨，开启新一局"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()