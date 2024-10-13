import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

from src.horse_pillar import HorsePillar
from src.read_race import RaceReader


def main():
    json = RaceReader.read("pred_streamlit.json")
    horse_pillar = HorsePillar(json)

    # セッション状態の初期化関数
    def initialize_session_state(key, default):
        if key not in st.session_state:
            st.session_state[key] = default

    # セッション状態の初期化
    initialize_session_state("horse_pillar", horse_pillar)
    initialize_session_state("year_list", horse_pillar.year_list)
    initialize_session_state("selected_year", horse_pillar.year_list[0])
    initialize_session_state("monthday_list", horse_pillar.monthday_list)
    initialize_session_state(
        "selected_monthday", horse_pillar.monthday_list[0]
    )
    initialize_session_state("jyo_list", horse_pillar.jyo_list)
    initialize_session_state("selected_jyo", horse_pillar.jyo_list[0])
    initialize_session_state("race_num_list", horse_pillar.race_num_list)
    initialize_session_state(
        "selected_race_num", horse_pillar.race_num_list[0]
    )
    initialize_session_state("change_select_box", False)
    initialize_session_state("df", pd.DataFrame())  # 追加
    initialize_session_state("selected_rows", [])  # 選択された行を保持

    def check_changing_select_box():
        st.session_state["change_select_box"] = True

    def update_select_box():
        horse_pillar = st.session_state["horse_pillar"]
        horse_pillar.set_race(
            st.session_state["selected_year"],
            st.session_state["selected_monthday"],
            st.session_state["selected_jyo"],
            st.session_state["selected_race_num"],
        )
        st.session_state["selected_year"] = horse_pillar.year
        st.session_state["selected_monthday"] = horse_pillar.monthday
        st.session_state["selected_jyo"] = horse_pillar.jyo
        st.session_state["selected_race_num"] = horse_pillar.race_num

        st.session_state["year_list"] = horse_pillar.year_list
        st.session_state["monthday_list"] = horse_pillar.monthday_list
        st.session_state["jyo_list"] = horse_pillar.jyo_list
        st.session_state["race_num_list"] = horse_pillar.race_num_list

    # セレクトボックスの設定
    select_boxes = [
        ("年", "year_list", "selected_year"),
        ("月日", "monthday_list", "selected_monthday"),
        ("競技場", "jyo_list", "selected_jyo"),
        ("レース番号", "race_num_list", "selected_race_num"),
    ]

    for label, list_key, selected_key in select_boxes:
        st.session_state[selected_key] = st.selectbox(
            label=label,
            options=st.session_state[list_key],
            on_change=check_changing_select_box,
            index=st.session_state[list_key].index(
                st.session_state[selected_key]
            ),
        )

    if st.session_state["change_select_box"]:
        update_select_box()
        st.session_state["change_select_box"] = False
        st.rerun()

    def parse_json(json_data):
        race = {k: v for k, v in json_data.items() if "uma" not in k}
        uma = pd.DataFrame(json_data["uma"]).T
        return race, uma

    race, uma = parse_json(st.session_state["horse_pillar"].get_horse_pillar())
    df = uma.reset_index(drop=True)

    # 単勝確率と複勝確率を数値として保持
    df["WinProbability"] = pd.to_numeric(df["WinProbability"], errors="coerce")
    df["ShowProbability"] = pd.to_numeric(
        df["ShowProbability"], errors="coerce"
    )

    # 必要な列を選択
    df = df[
        [
            "Umaban",
            "Bamei",
            "WinProbability",
            "ShowProbability",
            "Enable",
        ]
    ]

    # 列名を日本語にリネーム
    df.rename(
        columns={
            "Umaban": "馬番",
            "Bamei": "馬名",
            "WinProbability": "単勝確率",
            "ShowProbability": "複勝確率",
        },
        inplace=True,
    )

    # リネーム後に文字列としてフォーマット
    df["単勝確率"] = df["単勝確率"].map("{:.3f}".format)
    df["複勝確率"] = df["複勝確率"].map("{:.3f}".format)

    # 'Enable' 列でフィルタリングを削除
    # df = df[df["Enable"] == "True"].reset_index(drop=True)  # この行をコメントアウトまたは削除

    # レース情報の表示
    st.subheader(
        race["Title"]
        if race["Title"]
        else f"{race['Syubetu']} {race['Jyoken']}"
    )
    if race["Title"]:
        st.write(f"{race['Syubetu']} {race['Jyoken']}")
    st.write(f"発走時刻 {race['HassoTime'][:2]}:{race['HassoTime'][2:]}")
    st.write(f"芝 {race['Kyori']}m")

    # dfをセッション状態に保存
    st.session_state["df"] = df[
        ["馬番", "馬名", "単勝確率", "複勝確率"]
    ]  # 追加

    # AgGrid用の設定
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection(
        selection_mode="multiple",
        use_checkbox=True,
    )
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_default_column(
        sortable=True,
        filter=True,
        resizable=True,
    )

    # EnableがTrueの行にチェックを入れる
    pre_selected_rows = {umaban: umaban for umaban in df[df["Enable"]].index}

    gb.configure_column("Enable", hide=True)

    # 列幅を自動調整するための設定
    gb.configure_column("馬番", width=100)  # 馬番の幅を設定
    gb.configure_column("馬名", width=200)  # 馬名の幅を設定
    gb.configure_column("単勝確率", width=120)  # 単勝確率の幅を設定
    gb.configure_column("複勝確率", width=120)  # 複勝確率の幅を設定

    gb.configure_selection(
        selection_mode="multiple",
        use_checkbox=True,
        pre_selected_rows=pre_selected_rows,
    )

    grid_options = gb.build()

    # AgGridの表示
    grid_response = AgGrid(
        st.session_state["df"],
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,  # 必要に応じて設定
    )

    # 選択された行の取得
    selected = grid_response["selected_rows"]
    st.session_state["selected_rows"] = selected

    st.write("選択された馬:", st.session_state["selected_rows"])


if __name__ == "__main__":
    main()
