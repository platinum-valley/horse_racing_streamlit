import numpy as np
import pandas as pd
import streamlit as st

from src.horse_pillar import HorsePillar
from src.read_race import RaceReader


def main():
    json = RaceReader.read("race.json")
    horse_pillar = HorsePillar(json)

    if "horse_pillar" not in st.session_state:
        st.session_state["horse_pillar"] = horse_pillar
    # セッション状態の初期化（初回のみ実行）
    if "year_list" not in st.session_state:
        st.session_state["year_list"] = horse_pillar.year_list

    if "monthday_list" not in st.session_state:
        st.session_state["monthday_list"] = horse_pillar.monthday_list

    if "jyo_list" not in st.session_state:
        st.session_state["jyo_list"] = horse_pillar.jyo_list

    if "race_num_list" not in st.session_state:
        st.session_state["race_num_list"] = horse_pillar.race_num_list

    if "change_select_box" not in st.session_state:
        st.session_state["change_select_box"] = False

    def check_changing_select_box():
        st.session_state["change_select_box"] = True

    def update_select_box():
        # horse_pillarに対して、選択した情報とセット
        st.session_state["horse_pillar"].set_race(
            st.session_state["selected_year"],
            st.session_state["selected_monthday"],
            st.session_state["selected_jyo"],
            st.session_state["selected_race_num"],
        )
        # セットした情報をstreamlit上に反映
        st.session_state["selected_year"] = st.session_state["horse_pillar"].year
        st.session_state["selected_monthday"] = st.session_state[
            "horse_pillar"
        ].monthday
        st.session_state["selected_jyo"] = st.session_state["horse_pillar"].jyo
        st.session_state["selected_race_num"] = st.session_state[
            "horse_pillar"
        ].race_num

        # select boxで表示するリスト
        st.session_state["year_list"] = st.session_state["horse_pillar"].year_list
        st.session_state["monthday_list"] = st.session_state[
            "horse_pillar"
        ].monthday_list
        st.session_state["jyo_list"] = st.session_state["horse_pillar"].jyo_list
        st.session_state["race_num_list"] = st.session_state[
            "horse_pillar"
        ].race_num_list

    st.session_state["selected_year"] = st.selectbox(
        label="年",
        options=st.session_state.year_list,
        on_change=check_changing_select_box,
    )

    st.session_state["selected_monthday"] = st.selectbox(
        label="月日",
        options=st.session_state.monthday_list,
        on_change=check_changing_select_box,
    )

    st.session_state["selected_jyo"] = st.selectbox(
        label="競技場",
        options=st.session_state.jyo_list,
        on_change=check_changing_select_box,
    )

    st.session_state["selected_race_num"] = st.selectbox(
        label="レース番号",
        options=st.session_state.race_num_list,
        on_change=check_changing_select_box,
    )

    if st.session_state["change_select_box"]:
        update_select_box()
        st.session_state["change_select_box"] = False
        # [NOTE] ブラウザ上
        st.rerun()

    st.dataframe(st.session_state["horse_pillar"].get_horse_pillar())


if __name__ == "__main__":
    main()
