import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

from src.horse_pillar import HorsePillar
from src.read_race import RaceReader
from src.trifica_recomender import TrifectaRecommender


def main():
    json = RaceReader.read("pred_streamlit.json")
    horse_pillar = HorsePillar(json)
    recommender = TrifectaRecommender()

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

    # 2カラムレイアウトの作成
    col1, col2 = st.columns([6, 4])

    # AgGrid用のデータフレームを準備
    grid_df = df[["Enable", "馬番", "馬名", "単勝確率", "複勝確率"]].copy()

    # AgGrid用の設定
    gb = GridOptionsBuilder.from_dataframe(grid_df)

    # グリッドのオプション設定
    gb.configure_grid_options(
        pagination=True,  # ページネーションを有効化
        paginationPageSize=20,  # 1ページあたりの行数を50に設定
        domLayout="normal",  # 'normal'または'autoHeight'を指定
    )

    # その他の既存の設定
    gb.configure_default_column(
        resizable=True, filterable=False, sorteable=False, editable=False
    )

    # 列の設定
    gb.configure_column(
        "Enable",
        headerCheckboxSelection=False,  # ヘッダーにチェックボックスを表示
        checkboxSelection=False,  # 各行にチェックボックスを表示
        headerCheckboxSelectionFilteredOnly=False,
        width=50,
        hide=False,  # Enable列自体は非表示
    )
    gb.configure_column("馬番", width=100)
    gb.configure_column("馬名", width=200)
    gb.configure_column("単勝確率", width=120)
    gb.configure_column("複勝確率", width=120)

    # 選択行の初期値を設定
    gb.configure_grid_options(
        suppressRowClickSelection=True,  # チェックボックスのみで選択できるようにする
        rowSelection="multiple",  # 複数選択を許可
        preSelectedRows=grid_df[
            grid_df["Enable"]
        ].index.tolist(),  # Enableがtrueの行を事前選択
    )

    grid_options = gb.build()

    with col1:
        # AgGridの表示（高さを調整）
        grid_response = AgGrid(
            grid_df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True,
            theme="streamlit",
            height=400,  # 高さを調整
        )

    with col2:
        # 三連複馬券の推薦を表示
        st.subheader("🎫 三連複馬券の推奨買い目")

        # レースデータを取得して推薦を計算
        race_data = {
            str(i): {
                "Umaban": row["馬番"],
                "Enable": row["Enable"],
                "ShowProbability": float(row["複勝確率"]),
            }
            for i, row in grid_df.iterrows()
        }

        result = recommender.recommend_trifecta_bet(race_data)

        # 結果の表示
        if result["formation_type"]:
            st.write(f"**購入タイプ**: {result['formation_type']}")
            st.write(f"**購入点数**: {result['ticket_count']}点")

            if result["favorite"]:
                st.write(
                    "**メイン軸馬**: "
                    + ", ".join([f"[{num}]番" for num in result["favorite"]])
                )
            if result["second_favorite"]:
                st.write(
                    "**相手軸馬**: "
                    + ", ".join(
                        [f"[{num}]番" for num in result["second_favorite"]]
                    )
                )
            if result["other"]:
                st.write(
                    "**紐**: "
                    + ", ".join([f"[{num}]番" for num in result["other"]])
                )
        else:
            st.warning(result.get("message", "推奨買い目はありません"))

    # 選択された行を取得
    selected_rows = grid_response["selected_rows"]
    st.session_state["selected_rows"] = selected_rows


if __name__ == "__main__":
    main()
