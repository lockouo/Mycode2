import streamlit as st
import random
from openai import OpenAI
import time

# ==========================================
# 1. 页面全局配置与高级 CSS 样式 (打造神秘精致感)
# ==========================================
st.set_page_config(page_title="AI 塔罗占卜罗盘", layout="wide", initial_sidebar_state="collapsed")

# 注入 CSS 让网页充满高级的黑金神秘学氛围
st.markdown("""
<style>
    .stApp {
        background-color: #0d0e15;
        color: #e0e0e0;
    }
    .tarot-card {
        background: linear-gradient(145deg, #1a1c29 0%, #0d0e15 100%);
        border: 1px solid #c5a059;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 10px 20px rgba(197, 160, 89, 0.15);
        margin-bottom: 20px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        transition: transform 0.3s ease;
    }
    .tarot-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(197, 160, 89, 0.3);
    }
    .card-title {
        color: #c5a059;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
        font-family: 'Times New Roman', serif;
    }
    .card-type {
        color: #888;
        font-size: 14px;
        margin-bottom: 15px;
    }
    .position-upright { color: #4CAF50; font-weight: bold; font-size: 18px;}
    .position-reversed { color: #f44336; font-weight: bold; font-size: 18px;}
    .reversed-icon { transform: rotate(180deg); display: inline-block; }
    h1, h2, h3 { color: #c5a059 !important; text-align: center; font-family: 'Times New Roman', serif; }
</style>
""", unsafe_allow_html=True)

st.title("👁️‍🗨️ AI 命运织机：赛博塔罗占卜引擎")
st.markdown("### 提出你的困惑，让真随机概率与 AI 潜意识为你揭示未来的流向")
st.divider()

# ==========================================
# 2. 塔罗牌数据字典 (不依赖外部 API)
# ==========================================
MAJOR_ARCANA = ["愚者", "魔术师", "女祭司", "皇后", "皇帝", "教皇", "恋人", "战车", "力量", "隐士", 
                "命运之轮", "正义", "倒吊人", "死神", "节制", "恶魔", "高塔", "星星", "月亮", "太阳", "审判", "世界"]

SUITS = ["权杖 (行动/创造)", "圣杯 (情感/直觉)", "宝剑 (思想/冲突)", "星币 (物质/现实)"]
RANKS = ["王牌", "二", "三", "四", "五", "六", "七", "八", "九", "十", "侍从", "骑士", "王后", "国王"]
MINOR_ARCANA = [f"{suit}之{rank}" for suit in SUITS for rank in RANKS]

# ==========================================
# 3. 核心交互逻辑与会话状态管理
# ==========================================
# 使用 session_state 保证抽牌结果在网页刷新时不会丢失
if 'cards_drawn' not in st.session_state:
    st.session_state.cards_drawn = False
if 'drawn_data' not in st.session_state:
    st.session_state.drawn_data = {}

# 侧边栏输入 Key
st.sidebar.header("🔑 接入灵界 (API 配置)")
api_key = st.sidebar.text_input("请输入 DeepSeek API Key", type="password")

# 用户输入问题
question = st.text_input("第一步：在心中默念你的问题，并在此写下：", placeholder="例如：我接下来的职业发展方向应该如何抉择？")

# 抽牌按钮
if st.button("🔮 确认问题，由命运洗牌并抽取", use_container_width=True):
    if not question:
        st.warning("请先输入你想要占卜的问题！")
    else:
        with st.spinner("正在进行量子级真随机洗牌..."):
            time.sleep(1.5) # 增加仪式感
            
            # 保证真随机：抽取 3 张不重复的大阿卡那，9 张不重复的小阿卡那
            drawn_majors = random.sample(MAJOR_ARCANA, 3)
            drawn_minors = random.sample(MINOR_ARCANA, 9)
            
            # 为每张牌随机赋予正逆位
            positions = ["正位", "逆位"]
            
            spread = []
            for i in range(3):
                major = {
                    "name": drawn_majors[i],
                    "type": "大阿卡那 (核心命运)",
                    "position": random.choice(positions),
                    "minors": []
                }
                # 每张大牌分配 3 张小牌
                for j in range(3):
                    major["minors"].append({
                        "name": drawn_minors[i*3 + j],
                        "type": "小阿卡那 (细节/途径)",
                        "position": random.choice(positions)
                    })
                spread.append(major)
                
            st.session_state.drawn_data = spread
            st.session_state.cards_drawn = True

# ==========================================
# 4. 可视化展现牌阵 (精美 UI 渲染)
# ==========================================
if st.session_state.cards_drawn:
    st.divider()
    st.subheader("第二步：命运的展现 (你的专属牌阵)")
    
    # 渲染 HTML 卡片的辅助函数
    def render_card(card_data, is_major=True):
        pos_class = "position-upright" if card_data['position'] == "正位" else "position-reversed"
        icon_class = "" if card_data['position'] == "正位" else "reversed-icon"
        # 使用 Emoji 作为精美的占位符，替代真实的图片
        symbol = "🌌" if is_major else "✨" 
        
        return f"""
        <div class="tarot-card">
            <div class="{icon_class}" style="font-size: 40px; margin-bottom: 10px;">{symbol}</div>
            <div class="card-title">{card_data['name']}</div>
            <div class="card-type">{card_data['type']}</div>
            <div class="{pos_class}">[{card_data['position']}]</div>
        </div>
        """

    # 使用 Streamlit 的列布局，展现 3 组牌阵
    cols = st.columns(3)
    for i, col in enumerate(cols):
        with col:
            major_card = st.session_state.drawn_data[i]
            # 阶段标识
            stage_labels = ["过去 / 起因", "现在 / 现状", "未来 / 趋向"]
            st.markdown(f"### ✦ {stage_labels[i]} ✦")
            
            # 渲染大阿卡那
            st.markdown(render_card(major_card, is_major=True), unsafe_allow_html=True)
            
            # 渲染对应的小阿卡那
            st.markdown("<p style='text-align:center; color:#c5a059;'>👇 支撑此命运的三个细节 👇</p>", unsafe_allow_html=True)
            for minor_card in major_card['minors']:
                st.markdown(render_card(minor_card, is_major=False), unsafe_allow_html=True)

    st.divider()

    # ==========================================
    # 5. AI 解牌逻辑 (连接大模型)
    # ==========================================
    st.subheader("第三步：灵界潜意识解读")
    if st.button("🌌 召唤 AI 占卜师进行全盘解析", use_container_width=True):
        if not api_key:
            st.error("迷雾阻挡了视线：请在左侧边栏输入 DeepSeek API Key。")
        else:
            try:
                client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
                
                # 将抽牌数据结构化为提示词
                spread_info = ""
                stages = ["【过去/起因】", "【现在/现状】", "【未来/趋向】"]
                for i, major in enumerate(st.session_state.drawn_data):
                    minors_str = ", ".join([f"{m['name']}({m['position']})" for m in major['minors']])
                    spread_info += f"{stages[i]} 核心大牌：{major['name']}({major['position']}) | 辅助小牌：{minors_str}\n"

                prompt = f"""
                你是一位精通荣格心理学与古典神秘学的资深塔罗占卜师。
                问卜者的问题是：“{question}”
                
                经由命运洗牌，抽取的牌阵如下（按照过去、现在、未来的时间流展现）：
                {spread_info}
                
                请为问卜者进行深度的解牌。要求：
                1. 语气必须极其专业、神秘、富有哲理，具有治愈感和洞察力。
                2. 不要只是机械地罗列每张牌的通用含义，而是要将“大牌（命运大势）”与“三张小牌（具体细节、情绪或现实途径）”结合起来分析。
                3. 分析正逆位对能量流动的阻碍或促进作用。
                4. 最后给出一个切实可行、极具启发性的核心建议（不超过两句话）。
                排版要优美，使用适当的 Emoji 增强神秘感。
                """

                with st.spinner("AI 占卜师正在凝视你的牌阵，解读星象与命运的交织..."):
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": "你是一位拥有洞察人心能力的首席塔罗灵媒大师。"},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7 # 塔罗解读需要一定的创造力和发散思维
                    )
                    
                    st.success("命运的启示已降临：")
                    st.markdown(response.choices[0].message.content)

            except Exception as e:
                st.error(f"灵界连接中断：{e}")