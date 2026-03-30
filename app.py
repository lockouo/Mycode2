import streamlit as st
import random
import time
from openai import OpenAI

# ==========================================
# 1. 页面配置与高级 CSS 拟物牌面样式
# ==========================================
st.set_page_config(page_title="沉浸式赛博塔罗", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0a0b10; color: #d4af37; font-family: 'Times New Roman', serif; }
    h1, h2, h3 { color: #d4af37 !important; text-align: center; }
    
    /* 拟物化塔罗牌面设计 */
    .tarot-card-container {
        display: flex; flex-direction: column; align-items: center; margin-bottom: 20px;
    }
    .tarot-card {
        width: 160px; height: 260px; /* 经典塔罗牌比例 */
        background: linear-gradient(135deg, #1c1f2e 0%, #0a0b10 100%);
        border: 2px solid #8b6b22;
        border-radius: 12px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.8), inset 0 0 15px rgba(212, 175, 55, 0.2);
        display: flex; flex-direction: column; justify-content: space-between; align-items: center;
        padding: 15px 10px; position: relative;
        transition: transform 0.5s ease;
    }
    .tarot-card:hover { transform: translateY(-10px); box-shadow: 0 15px 30px rgba(212, 175, 55, 0.4); }
    
    /* 牌面元素 */
    .card-border-inner {
        position: absolute; top: 6px; left: 6px; right: 6px; bottom: 6px;
        border: 1px solid rgba(212, 175, 55, 0.5); border-radius: 8px; pointer-events: none;
    }
    .card-number { font-size: 14px; color: #a98d44; font-weight: bold; }
    .card-symbol { font-size: 60px; filter: drop-shadow(0 0 10px rgba(212, 175, 55, 0.5)); margin-top: 10px;}
    .card-name { font-size: 18px; color: #d4af37; font-weight: bold; text-align: center; margin-bottom: 5px;}
    
    /* 逆位翻转特效 */
    .is-reversed { transform: rotate(180deg); border-color: #8b2222; }
    .is-reversed .card-border-inner { border-color: rgba(139, 34, 34, 0.5); }
    .is-reversed:hover { transform: rotate(180deg) translateY(10px); }
    
    /* 单排释义文本框 */
    .meaning-box {
        background: rgba(28, 31, 46, 0.7); border-left: 3px solid #d4af37;
        padding: 12px; border-radius: 0 8px 8px 0; font-size: 14px; color: #e0e0e0;
        width: 100%; text-align: left; line-height: 1.5; margin-top: 10px;
    }
    .meaning-box.reversed-box { border-left-color: #8b2222; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 核心塔罗牌数据库 (修正名称与详细释义)
# ==========================================
# 提取大阿卡那数据
MAJORS_DATA = {
    "愚者": {"symbol": "🃏", "up": "无限可能、新的冒险、天真无畏、听从直觉。", "rev": "鲁莽冲动、逃避责任、计划不周、错失良机。"},
    "魔术师": {"symbol": "✨", "up": "创造力、化潜能为现实、沟通顺畅、资源充足。", "rev": "能力滥用、缺乏自信、沟通不畅、计划受阻。"},
    "女祭司": {"symbol": "🌙", "up": "直觉洞察、内在智慧、静待时机、潜意识的指引。", "rev": "直觉混乱、情感封闭、忽视内心的声音。"},
    "皇后": {"symbol": "👑", "up": "丰盛繁荣、母性滋养、创造力爆发、感官享受。", "rev": "过度溺爱、物质匮乏、创造力停滞、依赖他人。"},
    "皇帝": {"symbol": "🦅", "up": "建立秩序、规则与权威、领导力、坚实的物质基础。", "rev": "专制独裁、滥用职权、缺乏自律、秩序崩塌。"},
    "教皇": {"symbol": "🗝️", "up": "精神指引、传统价值观、教育与学习、贵人相助。", "rev": "盲目服从、打破传统、思想僵化、伪善。"},
    "恋人": {"symbol": "💞", "up": "灵魂契合、重要抉择、价值观共鸣、和谐的合作。", "rev": "关系破裂、错误的选择、价值观冲突、诱惑。"},
    "战车": {"symbol": "🐎", "up": "意志力、克服困难、胜利、强大的执行力。", "rev": "失去方向、力量失控、遇到阻碍、缺乏耐心。"},
    "力量": {"symbol": "🦁", "up": "内在勇气、温柔的控制、克服恐惧、耐心与包容。", "rev": "软弱无力、情绪失控、屈服于本能、缺乏自信。"},
    "隐士": {"symbol": "🏮", "up": "自我反思、寻求内在真理、孤独的沉淀、精神导师。", "rev": "孤僻自闭、逃避现实、拒绝他人的帮助。"},
    "命运之轮": {"symbol": "🎡", "up": "命运转折、不可抗拒的机遇、顺应周期、好运降临。", "rev": "厄运、抗拒改变、错失良机、处于低谷。"},
    "正义": {"symbol": "⚖️", "up": "公平公正、理性判断、因果法则、法律或合约事务。", "rev": "不公待遇、偏见、逃避责任、纠纷不利。"},
    "倒吊人": {"symbol": "🪢", "up": "换位思考、自愿牺牲、暂停与顿悟、以退为进。", "rev": "无谓的牺牲、钻牛角尖、抗拒现状、无法释怀。"},
    "死神": {"symbol": "💀", "up": "深刻蜕变、结束与新生、断舍离、必然的转变。", "rev": "抗拒改变、停滞不前、恐惧失去、难以放手。"},
    "节制": {"symbol": "🕊️", "up": "平衡调和、自我疗愈、跨界结合、适度与中庸。", "rev": "极端失衡、情绪波动、缺乏节制、沟通不良。"},
    "恶魔": {"symbol": "⛓️", "up": "物质诱惑、欲望束缚、成瘾、沉迷于表象。", "rev": "挣脱枷锁、摆脱控制、认清现实、重获自由。"},
    "高塔": {"symbol": "⚡", "up": "突如其来的灾难、固有信念的崩塌、毁灭性的觉醒。", "rev": "悬而未决的危机、逃避灾祸、重建的困难。"},
    "星星": {"symbol": "⭐", "up": "希望与疗愈、灵感涌现、宁静的指引、理想的愿景。", "rev": "绝望悲观、失去信心、灵感枯竭、好高骛远。"},
    "月亮": {"symbol": "🐺", "up": "潜意识的恐惧、迷惑与不安、隐藏的真相、直觉的波动。", "rev": "真相大白、克服恐惧、走出迷茫、情绪平复。"},
    "太阳": {"symbol": "☀️", "up": "纯粹的快乐、成功与荣耀、生命力旺盛、真相显现。", "rev": "成功延迟、短暂的快乐、缺乏热情、过度自信。"},
    "审判": {"symbol": "📯", "up": "觉醒与召唤、内心的救赎、客观的评估、业力清算。", "rev": "拒绝觉醒、自我怀疑、逃避评判、深陷自责。"},
    "世界": {"symbol": "🌍", "up": "完美的结局、圆满达成、进入新阶段、身心合一。", "rev": "功亏一篑、缺乏完满感、停滞在最后一步、眼界狭隘。"}
}

# 动态生成小阿卡那数据 (修正了名称格式)
SUITS_MAP = {
    "权杖": {"sym": "🌿", "core": "行动与创造"}, "圣杯": {"sym": "🏆", "core": "情感与直觉"},
    "宝剑": {"sym": "⚔️", "core": "思想与冲突"}, "星币": {"sym": "🪙", "core": "物质与现实"}
}
RANKS_MAP = {
    "一": "开端与潜能", "二": "选择与平衡", "三": "合作与成长", "四": "稳定与停滞", "五": "冲突与损失",
    "六": "和谐与过渡", "七": "挑战与防御", "八": "快速与转变", "九": "顶峰与焦虑", "十": "完结与重压",
    "侍从": "消息与探索", "骑士": "行动与冲动", "王后": "内在与滋养", "国王": "掌控与权威"
}

MINORS_DATA = {}
for suit, s_info in SUITS_MAP.items():
    for rank, r_mean in RANKS_MAP.items():
        name = f"{suit}{rank}" # 完美修正格式：如 "宝剑八"
        MINORS_DATA[name] = {
            "symbol": s_info["sym"],
            "up": f"【正位】在{s_info['core']}层面，体现出{r_mean}的正面能量。顺应此趋势行事。",
            "rev": f"【逆位】在{s_info['core']}层面，{r_mean}的能量受阻、过度或发生扭曲。需要反思调整。"
        }

# ==========================================
# 3. 仪式状态机 (控制一步步抽牌)
# ==========================================
# 初始化状态
if 'ritual_step' not in st.session_state:
    st.session_state.ritual_step = 0  # 步骤 0 到 7
    st.session_state.deck_majors = list(MAJORS_DATA.keys())
    st.session_state.deck_minors = list(MINORS_DATA.keys())
    random.shuffle(st.session_state.deck_majors)
    random.shuffle(st.session_state.deck_minors)
    st.session_state.spread = {"past": {}, "present": {}, "future": {}}

# ==========================================
# 4. 辅助函数：绘制拟物卡片与单排释义
# ==========================================
def render_tarot_card(name, is_major, position):
    data = MAJORS_DATA[name] if is_major else MINORS_DATA[name]
    is_rev = "is-reversed" if position == "逆位" else ""
    pos_color = "#8b2222" if position == "逆位" else "#d4af37"
    meaning_text = data["rev"] if position == "逆位" else data["up"]
    box_class = "reversed-box" if position == "逆位" else ""
    
    # 画牌
    card_html = f"""
    <div class="tarot-card-container">
        <div class="tarot-card {is_rev}">
            <div class="card-border-inner"></div>
            <div class="card-number">{"大阿卡那" if is_major else "小阿卡那"}</div>
            <div class="card-symbol">{data['symbol']}</div>
            <div class="card-name">{name}</div>
        </div>
        <div style="color: {pos_color}; font-weight: bold; margin-top: 5px;">[{position}]</div>
        <div class="meaning-box {box_class}">
            <b>释义：</b>{meaning_text}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# 抽牌逻辑
def draw_card(is_major):
    deck = st.session_state.deck_majors if is_major else st.session_state.deck_minors
    return {"name": deck.pop(), "position": random.choice(["正位", "逆位"])}

# ==========================================
# 5. UI 布局与交互流程
# ==========================================
st.title("👁️‍🗨️ AI 命运织机")
st.sidebar.header("🔑 接入灵界")
api_key = st.sidebar.text_input("DeepSeek API Key", type="password")
st.sidebar.markdown("---")
st.sidebar.info("仪式说明：\n1. 命运的展现需要时间。\n2. 请遵循指引，亲手完成每一次抽牌。\n3. 大牌决定宿命走向，小牌揭示现实途径。")

# 步骤 0：输入问题
if st.session_state.ritual_step == 0:
    question = st.text_input("在心中默念你的困惑，写下问题，然后开启仪式：")
    if st.button("开始洗牌与祈请", use_container_width=True):
        if not question:
            st.warning("请先输入问题！")
        else:
            st.session_state.question = question
            st.session_state.ritual_step = 1
            st.rerun()

# 步骤 1-6：手动抽牌仪式
if st.session_state.ritual_step > 0:
    st.markdown(f"**占卜命题：** {st.session_state.question}")
    st.divider()
    
    # 定义 3 个展示列
    col_past, col_present, col_future = st.columns(3)
    
    # 过去
    with col_past:
        st.subheader("✦ 过去 / 起因 ✦")
        if st.session_state.ritual_step == 1:
            if st.button("抽取第一张大阿卡那牌"):
                st.session_state.spread["past"]["major"] = draw_card(True)
                st.session_state.ritual_step = 2
                st.rerun()
                
        if st.session_state.ritual_step >= 2:
            render_tarot_card(st.session_state.spread["past"]["major"]["name"], True, st.session_state.spread["past"]["major"]["position"])
            
            if st.session_state.ritual_step == 2:
                if st.button("抽取三张小阿卡那牌 (补充过去)"):
                    st.session_state.spread["past"]["minors"] = [draw_card(False) for _ in range(3)]
                    st.session_state.ritual_step = 3
                    st.rerun()
            
            if st.session_state.ritual_step >= 3:
                st.markdown("<br><b>支撑细节：</b>", unsafe_allow_html=True)
                for m_card in st.session_state.spread["past"]["minors"]:
                    render_tarot_card(m_card["name"], False, m_card["position"])

    # 现在
    with col_present:
        st.subheader("✦ 现在 / 现状 ✦")
        if st.session_state.ritual_step == 3:
            if st.button("抽取第二张大阿卡那牌"):
                st.session_state.spread["present"]["major"] = draw_card(True)
                st.session_state.ritual_step = 4
                st.rerun()
                
        if st.session_state.ritual_step >= 4:
            render_tarot_card(st.session_state.spread["present"]["major"]["name"], True, st.session_state.spread["present"]["major"]["position"])
            
            if st.session_state.ritual_step == 4:
                if st.button("抽取三张小阿卡那牌 (补充现在)"):
                    st.session_state.spread["present"]["minors"] = [draw_card(False) for _ in range(3)]
                    st.session_state.ritual_step = 5
                    st.rerun()
                    
            if st.session_state.ritual_step >= 5:
                st.markdown("<br><b>支撑细节：</b>", unsafe_allow_html=True)
                for m_card in st.session_state.spread["present"]["minors"]:
                    render_tarot_card(m_card["name"], False, m_card["position"])

    # 未来
    with col_future:
        st.subheader("✦ 未来 / 趋向 ✦")
        if st.session_state.ritual_step == 5:
            if st.button("抽取第三张大阿卡那牌"):
                st.session_state.spread["future"]["major"] = draw_card(True)
                st.session_state.ritual_step = 6
                st.rerun()
                
        if st.session_state.ritual_step >= 6:
            render_tarot_card(st.session_state.spread["future"]["major"]["name"], True, st.session_state.spread["future"]["major"]["position"])
            
            if st.session_state.ritual_step == 6:
                if st.button("抽取三张小阿卡那牌 (补充未来)"):
                    st.session_state.spread["future"]["minors"] = [draw_card(False) for _ in range(3)]
                    st.session_state.ritual_step = 7
                    st.rerun()
                    
            if st.session_state.ritual_step >= 7:
                st.markdown("<br><b>支撑细节：</b>", unsafe_allow_html=True)
                for m_card in st.session_state.spread["future"]["minors"]:
                    render_tarot_card(m_card["name"], False, m_card["position"])

# ==========================================
# 6. 第 7 步：AI 全盘解牌
# ==========================================
if st.session_state.ritual_step == 7:
    st.divider()
    if st.button("🌌 仪式完成，呼唤 AI 灵媒进行全盘解读", use_container_width=True):
        if not api_key:
            st.error("请在左侧边栏输入 DeepSeek API Key 以连接灵界。")
        else:
            try:
                client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
                
                # 构造给 AI 的数据结构
                prompt_info = ""
                for stage, s_name in zip(["past", "present", "future"], ["【过去】", "【现在】", "【未来】"]):
                    data = st.session_state.spread[stage]
                    minors_str = ", ".join([f"{m['name']}({m['position']})" for m in data['minors']])
                    prompt_info += f"{s_name} 主牌：{data['major']['name']}({data['major']['position']}) | 辅牌：{minors_str}\n"

                prompt = f"""
                你是一位精通神秘学的首席塔罗占卜师。
                问卜者的问题是：“{st.session_state.question}”
                
                牌阵如下：
                {prompt_info}
                
                请提供深度解读。要求：
                1. 语气神秘、专业、极具洞察力。
                2. 分析每个时间阶段时，必须解释“大阿卡那（主基调）”是如何通过“三张小阿卡那（具体行为/细节）”在现实中运作的。
                3. 注意正逆位对能量的改变。
                4. 最后给出一个醍醐灌顶的核心建议。
                """

                with st.spinner("灵媒正在倾听卡牌的低语..."):
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": "你是一位拥有洞穿宿命能力的塔罗大师。"},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    st.success("命运的启示：")
                    st.markdown(response.choices[0].message.content)

            except Exception as e:
                st.error(f"灵界连接中断：{e}")
                
    # 重置按钮
    if st.button("重新开始新的占卜"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()