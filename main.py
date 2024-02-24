import numpy as np
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, AgGridTheme, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

from src.horse_pillar import HorsePillar
from src.read_race import RaceReader


def main():
    json = RaceReader.read("pred_streamlit.json")
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

    def parse_json(json):
        race = {key: json[key] for key in json.keys() if "uma" not in key}
        uma = pd.DataFrame(json["uma"]).T
        return race, uma

    race, uma = parse_json(st.session_state["horse_pillar"].get_horse_pillar())
    df = uma
    df["Enable"] = ""
    df["ShowProbability"] = df["ShowProbability"].apply(lambda x: "{:.3f}".format(x))
    df = df[
        [
            "Enable",
            "Wakuban",
            "Umaban",
            "Bamei",
            "Sex",
            "Kisyumei",
            "Futan",
            "ShowProbability",
        ]
    ].astype(str)
    df = df.rename(
        columns={
            "Wakuban": "枠番",
            "Umaban": "馬番",
            "Bamei": "馬名",
            "Sex": "性別",
            "Kisyumei": "騎手名",
            "Futan": "斤量",
            "ShowProbability": "複勝確率",
        }
    )

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection(
        selection_mode="multiple", use_checkbox=True, pre_select_all_rows=True
    )
    for col in df.columns:
        max_length = df[col].map(len).max()
        # 最大文字数に基づいて幅を設定（例: 1文字あたり10ピクセル + 30ピクセルのマージン）
        col_width = str(max_length * 15 + 50)
        gb.configure_column(col, width=col_width)

    grid_options = gb.build()

    st.subheader(
        race["Title"] if race["Title"] != "" else f"{race['Syubetu']} {race['Jyoken']}"
    )
    st.write(f"{race['Syubetu']} {race['Jyoken']}" if race["Title"] != "" else "")
    st.write(f"発走時刻 {race['HassoTime'][:2]}:{race['HassoTime'][2:]}")
    st.write(f"芝 {race['Kyori']}m")

    # AgGridにグリッドオプションを渡して、データフレームを表示
    grid_table = AgGrid(
        df,
        gridOptions=grid_options,
        theme="streamlit",
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=False,
    )


if __name__ == "__main__":
    main()
