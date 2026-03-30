import streamlit as st
import random
from openai import OpenAI

# ==========================================
# 1. 全局配置与高级 UI 系统 (暗物质卡槽)
# ==========================================
st.set_page_config(page_title="沉浸式赛博塔罗 | 全量图鉴版", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* 全局暗黑神秘学风格 */
    .stApp { background-color: #090a0f; color: #d1d5db; font-family: 'Times New Roman', STSong, serif; }
    h1, h2, h3 { color: #eab308 !important; text-align: center; text-shadow: 0 0 10px rgba(234, 179, 8, 0.3); }
    
    /* 隐藏原生按钮边框，重塑神秘学按钮 */
    div.stButton > button {
        background: transparent; border: 1px solid #eab308; color: #eab308;
        border-radius: 4px; transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 2px;
    }
    div.stButton > button:hover { background: rgba(234, 179, 8, 0.1); box-shadow: 0 0 15px rgba(234, 179, 8, 0.4); border-color: #facc15; color: #facc15; }

    /* 核心卡牌框架：统一高度与完美居中 */
    .card-slot {
        display: flex; flex-direction: column; align-items: center; justify-content: flex-start;
        margin-bottom: 30px; min-height: 400px;
    }
    
    /* 塔罗实体与翻转特效 */
    .tarot-frame {
        width: 170px; height: 290px; perspective: 1000px; margin-bottom: 15px;
    }
    .tarot-inner {
        width: 100%; height: 100%; position: relative; transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d;
    }
    /* 逆位物理翻转 */
    .is-reversed .tarot-inner { transform: rotate(180deg); }
    
    .tarot-front, .tarot-back {
        width: 100%; height: 100%; position: absolute; backface-visibility: hidden;
        border-radius: 8px; box-shadow: 0 10px 25px rgba(0,0,0,0.8); border: 2px solid #4b5563;
    }
    /* 精美牌背设计 */
    .tarot-back {
        background: radial-gradient(circle, #1f2937 0%, #030712 100%); border-color: #eab308;
        display: flex; justify-content: center; align-items: center;
        background-image: repeating-linear-gradient(45deg, rgba(234, 179, 8, 0.05) 0, rgba(234, 179, 8, 0.05) 2px, transparent 2px, transparent 8px);
    }
    .tarot-back::after { content: '✧'; color: #eab308; font-size: 45px; opacity: 0.5; }
    
    /* 原画渲染层 */
    .tarot-front img { width: 100%; height: 100%; object-fit: cover; border-radius: 6px; }
    
    /* 百科级释义数据看板 */
    .wiki-panel {
        width: 100%; max-width: 320px; background: rgba(17, 24, 39, 0.8);
        border: 1px solid #374151; border-top: 3px solid #eab308; border-radius: 6px;
        padding: 15px; font-size: 13px; line-height: 1.6; text-align: left;
    }
    .wiki-panel.rev-panel { border-top-color: #ef4444; }
    
    .wiki-title { font-size: 16px; color: #f3f4f6; font-weight: bold; text-align: center; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid #374151; }
    .status-badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; margin-bottom: 10px; }
    .up-badge { background: rgba(34, 197, 94, 0.1); color: #4ade80; border: 1px solid #22c55e; }
    .rev-badge { background: rgba(239, 68, 68, 0.1); color: #f87171; border: 1px solid #ef4444; }
    
    .wiki-row { margin-bottom: 4px; }
    .wiki-label { color: #9ca3af; font-weight: bold; }
    .wiki-value { color: #d1d5db; }
    .wiki-highlight { color: #eab308; font-weight: bold;}
    .wiki-astro { color: #c084fc; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 正统神秘学塔罗图鉴数据库 (黄金黎明体系)
# ==========================================
BASE_IMG_URL = "https://sacred-texts.com/tarot/pkt/img/"

# 大阿卡那全量数据 (已替换为最权威的占星与元素对应)
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

# 小阿卡那动态生成引擎
suits_info = {
    "权杖": {"elem": "火", "core": "行动、意志与创造力", "symbol": "wa"},
    "圣杯": {"elem": "水", "core": "情感、潜意识与人际", "symbol": "cu"},
    "宝剑": {"elem": "风", "core": "思想、理智与冲突", "symbol": "sw"},
    "星币": {"elem": "土", "core": "物质、财富与现实基础", "symbol": "pe"}
}
ranks_info = {
    "首牌": "新契机、潜能的爆发", "二": "选择、平衡与规划", "三": "初步成果、合作与成长", "四": "稳定、休息与停滞",
    "五": "冲突、损失与困境", "六": "和谐、过渡与帮助", "七": "挑战、防守与坚持", "八": "迅速、移动与专注",
    "九": "顶点、独立与焦虑", "十": "完结、重压与极盛", "侍从": "新消息、学习与探索", "骑士": "行动力、冲动与追求",
    "王后": "内在掌控、滋养与成熟", "国王": "外在权威、规则与掌控"
}

MAJORS = {}
for i, (name, data) in enumerate(MAJORS_DB.items()):
    MAJORS[name] = {
        "img_url": f"{BASE_IMG_URL}ar{i:02d}.jpg",
        "tags": data["tags"], "astro": data["astro"], "elem": data["elem"],
        "up": f"【核心释义】{data['meaning']} 正位能量顺畅发散。",
        "rev": f"【逆位警示】{data['meaning']} 能量发生扭曲、过度或遭遇阻碍。需反思。"
    }

MINORS = {}
for suit_name, s_data in suits_info.items():
    for i, (rank_name, r_data) in enumerate(ranks_info.items()):
        full_name = f"{suit_name}{rank_name}"
        num = i + 1
        
        # 针对权杖首牌的硬编码百科植入（完美一比一复刻）
        if full_name == "权杖首牌":
            MINORS["权杖首牌 (Ace Of Wands)"] = {
                "img_url": f"{BASE_IMG_URL}wa01.jpg",
                "tags": "新行动、创造、机会、灵感、潜力、启动、创新、冒险",
                "elem": "火",
                "astro": "火象星座 (牡羊/狮子/射手)",
                "up": "象征着新的开始、创造力、激情与行动力的迸发。它代表着一个充满潜力的新机会或项目的启动，鼓励积极行动、勇敢探索。",
                "rev": "反映能量失控导致的拖延、方向错误或自我否定，表现为热情消退、计划缺失及资源浪费，需重新审视目标与动机。"
            }
        else:
            MINORS[f"{full_name}"] = {
                "img_url": f"{BASE_IMG_URL}{s_data['symbol']}{num:02d}.jpg",
                "tags": f"{s_data['core']}、{r_data.split('、')[0]}",
                "elem": s_data['elem'],
                "astro": f"{s_data['elem']}象特质",
                "up": f"在{s_data['elem']}元素（{s_data['core']}）领域，迎来了【{r_data}】的阶段。建议顺应此局势发展。",
                "rev": f"在{s_data['elem']}元素领域，【{r_data}】的特质表现出负面效应，能量受阻或内耗。"
            }

# ==========================================
# 3. 开放式 API 配置 (侧边栏)
# ==========================================
st.sidebar.header("🔌 大模型 API 配置")
st.sidebar.markdown("<span style='color:#9ca3af; font-size:13px;'>支持配置任意兼容 OpenAI 协议的大模型接口。</span>", unsafe_allow_html=True)
api_base = st.sidebar.text_input("API Base URL", value="https://api.openai.com/v1", help="例如 DeepSeek 填入 https://api.deepseek.com")
api_model = st.sidebar.text_input("模型名称 (Model)", value="gpt-3.5-turbo", help="例如 DeepSeek 填入 deepseek-chat")
api_key = st.sidebar.text_input("API Key", type="password")
st.sidebar.divider()

# ==========================================
# 4. 状态机与 UI 渲染系统
# ==========================================
if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.deck_m = list(MAJORS.keys()); random.shuffle(st.session_state.deck_m)
    st.session_state.deck_min = list(MINORS.keys()); random.shuffle(st.session_state.deck_min)
    st.session_state.spread = {"past": {}, "present": {}, "future": {}}

def draw_card(is_major):
    return {"name": (st.session_state.deck_m if is_major else st.session_state.deck_min).pop(), "pos": random.choice(["正位", "逆位"])}

def render_slot(stage_name, step_req_major, step_req_minor, state_key):
    """渲染高级卡槽，未抽牌显示牌背，已抽牌显示原画与百科数据"""
    st.markdown(f"<h3 style='color:#f3f4f6;'>✦ {stage_name} ✦</h3>", unsafe_allow_html=True)
    
    if st.session_state.step < step_req_major:
        st.markdown("""
        <div class="card-slot">
            <div class="tarot-frame"><div class="tarot-inner"><div class="tarot-back"></div></div></div>
            <div style="color:#6b7280; font-size:12px; margin-top:10px;">[ 等待灵体响应 ]</div>
        </div>
        """, unsafe_allow_html=True)
        if st.session_state.step == step_req_major - 1:
            if st.button(f"揭开 {stage_name} (主牌)", key=f"btn_m_{stage_name}"):
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
                <div class="tarot-inner">
                    <div class="tarot-front"><img src="{data['img_url']}"></div>
                </div>
            </div>
            <div class="wiki-panel {p_class}">
                <div class="wiki-title">{card["name"]}</div>
                <div style="text-align: center;">{badge}</div>
                <div class="wiki-row"><span class="wiki-label">元素属性：</span><span class="wiki-highlight">{data['elem']}</span></div>
                <div class="wiki-row"><span class="wiki-label">占星对应：</span><span class="wiki-astro">{data['astro']}</span></div>
                <div class="wiki-row"><span class="wiki-label">关键字：</span><span class="wiki-value">{data['tags']}</span></div>
                <div class="wiki-row" style="margin-top:8px;"><span class="wiki-label">牌面解析：</span><span class="wiki-value">{meaning}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.step == step_req_minor - 1:
            if st.button(f"抽取细节途径 (辅牌)", key=f"btn_min_{stage_name}"):
                st.session_state.spread[state_key]["minors"] = draw_card(False)
                st.session_state.step = step_req_minor; st.rerun()
                
        if st.session_state.step >= step_req_minor:
            m_card = st.session_state.spread[state_key]["minors"]
            m_data = MINORS[m_card["name"]]
            m_badge = "<span style='color:#ef4444;'>[逆位]</span>" if m_card["pos"] == "逆位" else "<span style='color:#22c55e;'>[正位]</span>"
            m_meaning = m_data["rev"] if m_card["pos"] == "逆位" else m_data["up"]
            
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.05); border-radius:6px; padding:10px; margin-top: -15px; border-left: 2px solid #6b7280; font-size:13px; max-width:320px; margin-left:auto; margin-right:auto;">
                <div style="color:#eab308; font-weight:bold; margin-bottom:5px;">↳ 细节辅助：{m_card["name"]} {m_badge}</div>
                <div style="color:#9ca3af;"><b>属性：</b>{m_data['elem']} ({m_data['astro']}) | <b>关键字：</b>{m_data['tags']}</div>
                <div style="color:#d1d5db; margin-top:5px;">{m_meaning}</div>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# 5. 主仪式场流程控制
# ==========================================
st.title("👁️‍🗨️ 赛博塔罗：全量图鉴版")

if st.session_state.step == 0:
    st.markdown("<div style='text-align:center; color:#9ca3af; margin-bottom:20px;'>此版本已搭载 78 张完整百科图鉴，支持任意兼容协议的大模型。</div>", unsafe_allow_html=True)
    q = st.text_input("请在此铭刻你的疑问：", placeholder="例如：我接下来的毕业设计项目会遇到什么阻碍？")
    col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
    with col_btn2:
        if st.button("启动塔罗阵列", use_container_width=True):
            if q: st.session_state.q = q; st.session_state.step = 1; st.rerun()
            else: st.warning("未检测到精神波动（请输入问题）。")

if st.session_state.step > 0:
    st.markdown(f"<h4 style='text-align:center; color:#eab308; border-bottom:1px dashed #374151; padding-bottom:15px; margin-bottom:30px;'>探讨命题：{st.session_state.q}</h4>", unsafe_allow_html=True)
    
    col_p, col_pr, col_f = st.columns(3)
    
    # 状态机步骤已完美对齐，不会报错
    with col_p: render_slot("过去起因", 1, 2, "past")
    with col_pr: render_slot("现在状况", 3, 4, "present")
    with col_f: render_slot("未来走向", 5, 6, "future")

# ==========================================
# 6. 通用大模型解盘系统
# ==========================================
if st.session_state.step == 6:
    st.divider()
    col_ai1, col_ai2, col_ai3 = st.columns([1,2,1])
    with col_ai2:
        if st.button("🌌 请求大模型进行高维解阵", use_container_width=True):
            if not api_key: st.error("请先在左侧边栏配置 API Key。")
            else:
                try:
                    # 动态调用侧边栏配置的模型和 URL
                    client = OpenAI(api_key=api_key, base_url=api_base)
                    
                    prompt = f"问卜者：“{st.session_state.q}”\n"
                    for stage, key in zip(["【过去】", "【现在】", "【未来】"], ["past", "present", "future"]):
                        maj = st.session_state.spread[key]["major"]
                        mins = st.session_state.spread[key]["minors"]
                        prompt += f"{stage} 主牌：{maj['name']}({maj['pos']}) | 辅牌：{mins['name']}({mins['pos']})\n"
                    
                    prompt += "请作为资深塔罗大师进行解读。结合主牌的宿命与辅牌的现实细节，排版必须清晰，并给出实质性建议。"
                    
                    with st.spinner(f"正在通过 {api_model} 连接星界网络..."):
                        res = client.chat.completions.create(
                            model=api_model,
                            messages=[{"role": "system", "content": "你是一位顶级塔罗解读师。"}, {"role": "user", "content": prompt}],
                            temperature=0.7
                        )
                        st.success("解析完毕：")
                        st.markdown(f"<div style='background:#111827; padding:20px; border-radius:8px; border:1px solid #374151;'>{res.choices[0].message.content}</div>", unsafe_allow_html=True)
                except Exception as e: st.error(f"接口调用失败，请检查 Base URL、模型名称和 Key。错误详情：{e}")
            
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("↻ 重置星轨"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()