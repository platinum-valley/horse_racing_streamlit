import streamlit as st

A = ["東京", "京都"]
B = {
    "東京": ["渋谷", "新宿", "品川"],
    "京都": ["伏見", "宇治"],
}


selected_A = st.selectbox(
    "都道府県",
    options=A,
)
selected_B = st.selectbox("都市", options=B[selected_A])

selected_A
selected_B
