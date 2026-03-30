# ==========================================
# 6. 大模型综合解盘 (样式优化版)
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
                    
                    # 强化 Prompt：要求 AI 必须分段输出，避免一长串
                    prompt = f"问卜者的问题是：【{st.session_state.q}】。\n"
                    prompt += "请作为资深塔罗大师，针对问卜者的具体问题进行解牌：\n\n"
                    for stage, key in zip(["【过去起因】", "【现在状况】", "【未来走向】"], ["past", "present", "future"]):
                        maj = st.session_state.spread[key]["major"]
                        mins = st.session_state.spread[key]["minors"]
                        mins_str = "、".join([f"{m['name']}({m['pos']})" for m in mins])
                        prompt += f"{stage} 宿命主牌：{maj['name']}({maj['pos']}) | 现实辅牌：{mins_str}\n"
                    
                    prompt += """
                    \n解读要求：
                    1. 必须分三个章节输出：### 🔮 灵界基调、### ⌛ 时间流推演、### 🕯️ 命运指引。
                    2. 语气要神秘且专业，不要说废话，段落之间要有明显的空行。
                    3. 针对问卜者的问题给出实质性回答。
                    """
                    
                    with st.spinner(f"正在建立精神连接..."):
                        res = client.chat.completions.create(
                            model=api_model,
                            messages=[{"role": "system", "content": f"你是一位精通神秘学的塔罗大师。"}, {"role": "user", "content": prompt}],
                            temperature=0.7
                        )
                        st.success("命运之书已翻开：")
                        
                        # --- 核心样式优化区 ---
                        ai_style = """
                        <div style="
                            background: linear-gradient(145deg, rgba(28,32,48,0.9), rgba(13,17,23,0.95));
                            border: 1px solid rgba(234, 179, 8, 0.3);
                            border-radius: 12px;
                            padding: 35px;
                            box-shadow: 0 15px 35px rgba(0,0,0,0.5), inset 0 0 20px rgba(234,179,8,0.05);
                            backdrop-filter: blur(10px);
                            line-height: 1.8;
                            color: #e2e8f0;
                            max-width: 900px;
                            margin: 20px auto;
                            text-align: left;
                        ">
                        """
                        # 使用 streamlit 渲染经过样式包装后的 AI 内容
                        st.markdown(ai_style + res.choices[0].message.content + "</div>", unsafe_allow_html=True)
                        # --------------------
                        
                except Exception as e: st.error(f"接口调用失败。错误详情：{e}")
            
    st.markdown("<br>", unsafe_allow_html=True)
    col_r1, col_r2, col_r3 = st.columns([1, 1, 1])
    with col_r2:
        if st.button("↻ 结束本次占卜", use_container_width=True):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()