import json
from math import comb


class TrifectaRecommender:
    """3連複(馬券)の推奨買い目を作成するクラス。

    Attributes:
        same_threshold (float): トップ馬の入着確率との誤差がこの値以内であれば
            「軸馬候補」とみなす閾値。
    """

    def __init__(self, same_threshold=0.05):
        """
        Args:
            same_threshold (float, optional): トップ馬との入着確率の差が
                この値以内なら「軸馬候補」とみなす。デフォルトは 0.05。
        """
        self.same_threshold = same_threshold

    def recommend_trifecta_bet(self, race_data):
        """3連複馬券の推奨買い目を作成し、購入点数とともに返す。

        馬ごとの情報を事前に
          - favorite(メイン軸馬)
          - second_favorite(相手軸馬)
          - other(紐)
        に振り分けたうえで、提示されたパターンを照合します。

        Google Style:
        Args:
            race_data (dict): 馬ごとの情報を含む辞書。例)
                {
                  "0": {
                    "Umaban": "01",
                    "Enable": true,
                    "ShowProbability": 0.3916
                  },
                  "1": {
                    "Umaban": "02",
                    "Enable": false,
                    "ShowProbability": 0.2074
                  },
                  ...
                }

        Returns:
            dict:
                - "formation_type" (str|None):
                  - "3連複1頭軸"
                  - "3連複2頭軸"
                  - "3連複ボックス"
                  - "3連複フォーメーション"
                  - None（購入しない場合）
                - "favorite" (list[str]): メイン軸馬
                - "second_favorite" (list[str]): 相手軸馬
                - "other" (list[str]): 紐
                - "ticket_count" (int): 購入点数
                - "message" (str, optional): 補足説明や購入見送り理由など
        """
        # ---------- 1) Enable==True の馬だけ抽出し、入着確率が高い順に並べる ----------
        horses_enabled = []
        for _, info in race_data.items():
            if info["Enable"]:
                umaban = info["Umaban"]
                sp = info["ShowProbability"]
                horses_enabled.append((umaban, sp))

        if not horses_enabled:
            return {
                "formation_type": None,
                "favorite": [],
                "second_favorite": [],
                "other": [],
                "ticket_count": 0,
                "message": "Enable=True の馬がいません。",
            }

        # 入着確率が高い順にソート
        horses_enabled.sort(key=lambda x: x[1], reverse=True)

        # トップ馬(最も入着確率が高い馬)の確率
        top_umaban, top_showprob = horses_enabled[0]

        # ---------- 2) favorite / second_favorite / other に振り分け ----------
        favorite = []
        second_favorite = []
        for umaban, sp in horses_enabled:
            diff = abs(sp - top_showprob)
            if diff <= 0.01:
                # トップ馬と 0.01差以内
                favorite.append(umaban)
            elif diff <= self.same_threshold:
                # トップ馬と 0.01超 ～ same_threshold差以内
                second_favorite.append(umaban)
            else:
                # 軸候補からは外れる
                pass

        used_as_axis = set(favorite + second_favorite)
        other = [
            umaban
            for (umaban, _) in horses_enabled
            if umaban not in used_as_axis
        ]

        # ---------- 3) パターン判定の準備 ----------
        f_count = len(favorite)
        s_count = len(second_favorite)
        o_count = len(other)

        # チケット点数を計算する変数
        ticket_count = 0
        formation_type = None

        # ---------- 4) 提示された各パターンに該当するかを順番に判定 ----------
        #
        # 3連複1頭軸パターン
        #   (1) favorite=1, second=0, other>=2
        #   (2) favorite=1, second>=3, other=0
        #   (3) favorite=1, second>=4, other>=1
        if f_count == 1 and s_count == 0 and o_count >= 2:
            formation_type = "3連複1頭軸"
            ticket_count = comb(o_count, 2)  # 紐から2頭選ぶ組合せ

        elif f_count == 1 and s_count >= 3:
            formation_type = "3連複1頭軸"
            ticket_count = comb(s_count, 2)  # 相手軸馬から2頭選ぶ組合せ

        elif f_count == 1 and s_count >= 2 and o_count >= 1:
            formation_type = "3連複1頭軸"
            total = s_count + o_count
            ticket_count = comb(total, 2)  # 相手軸+紐 の中から2頭選ぶ組合せ

        # 3連複2頭軸パターン
        #   (1) favorite=1, second=1, other>=1
        #   (2) favorite=2, second>=1, other=0
        #   (3) favorite=2, second=0, other>=2
        elif f_count == 1 and s_count == 1 and o_count >= 1:
            formation_type = "3連複2頭軸"
            # 軸2頭固定 + 紐から1頭選ぶ
            ticket_count = o_count

        elif f_count == 2 and s_count >= 1:
            formation_type = "3連複2頭軸"
            # 軸2頭固定 + 相手軸複数 => その中から1頭選ぶ
            ticket_count = s_count

        elif f_count == 2 and o_count >= 2:
            formation_type = "3連複2頭軸"
            # 軸2頭固定 + 紐から1頭選ぶ
            ticket_count = o_count

        elif f_count == 2 and s_count >= 1 and o_count >= 1:
            formation_type = "3連複2頭軸"
            # 軸2頭固定 + 紐から1頭選ぶ
            total = s_count + o_count
            ticket_count = comb(total, 2)

        # 3連複ボックスパターン
        #   (1) favorite>=3, second=0, other=0
        elif f_count >= 3:
            formation_type = "3連複ボックス"
            ticket_count = comb(f_count, 3)  # favoriteだけでBOX組む

        # 3連複フォーメーションパターン
        #   (1) favorite=1, second=2~3, other>=1
        #   (2) favorite=2~3, second>=1, other>=1
        elif (f_count == 1 and 2 <= s_count <= 3 and o_count >= 1) or (
            2 <= f_count <= 3 and s_count >= 1 and o_count >= 1
        ):
            formation_type = "3連複フォーメーション"
            # フォーメーションの点数は一律の暫定計算とし、詳細ロジックは各自拡張可
            # 例: 軸馬( favorite + second_favorite )のうち3頭 or 2頭 + other など
            # ここでは簡易的に「second_favorite + other の中から2頭選ぶ」としておく
            total = s_count + o_count
            if total >= 2:
                ticket_count = comb(total, 2)
            else:
                ticket_count = 0

        else:
            # 上記パターンのいずれにも当てはまらない場合は「購入しない」とする
            return {
                "formation_type": None,
                "favorite": favorite,
                "second_favorite": second_favorite,
                "other": other,
                "ticket_count": 0,
                "message": "提示されたパターンに該当しません。",
            }

        # ---------- 5) 購入点数が21点を超えたら見送り ----------
        if ticket_count > 21:
            return {
                "formation_type": None,
                "favorite": favorite,
                "second_favorite": second_favorite,
                "other": other,
                "ticket_count": ticket_count,
                "message": f"購入点数({ticket_count}点)が21点を超えるため見送ります。",
            }

        # ---------- 6) 結果返却 ----------
        return {
            "formation_type": formation_type,
            "favorite": favorite,
            "second_favorite": second_favorite,
            "other": other,
            "ticket_count": ticket_count,
        }


# ------------------------------------------------------------------------------
# 実行サンプル（テスト用）
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    data_str = """
    {
        "1201": {
            "06": {
                "03": {
                    "Year": "2024",
                    "MonthDay": "1201",
                    "HassoTime": "1105",
                    "JyoCD": "06",
                    "Kyori": 1600,
                    "Title": "",
                    "uma": {
                        "0": {
                            "Umaban": "01",
                            "Enable": true,
                            "Wakuban": "1",
                            "Futan": 54,
                            "WinProbability": 0.18653683644855093,
                            "ShowProbability": 0.39165491090377075
                        },
                        "1": {
                            "Umaban": "02",
                            "Enable": false,
                            "Wakuban": "2",
                            "WinProbability": 0.09109817313268985,
                            "ShowProbability": 0.20742625332816816
                        },
                        "2": {
                            "Umaban": "03",
                            "Enable": false,
                            "Wakuban": "2",
                            "WinProbability": 0.12623702030272685,
                            "ShowProbability": 0.20173491245281133
                        },
                        "3": {
                            "Umaban": "04",
                            "Enable": false,
                            "Wakuban": "3",
                            "WinProbability": 0.09615489902797175,
                            "ShowProbability": 0.1857666630440445
                        },
                        "4": {
                            "Umaban": "05",
                            "Enable": true,
                            "Wakuban": "3",
                            "WinProbability": 0.11420924872022506,
                            "ShowProbability": 0.3807301833246683
                        },
                        "5": {
                            "Umaban": "06",
                            "Enable": false,
                            "Wakuban": "4",
                            "WinProbability": 0.03922338863438813,
                            "ShowProbability": 0.0807813271934426
                        },
                        "6": {
                            "Umaban": "07",
                            "Enable": false,
                            "Wakuban": "4",
                            "WinProbability": 0.09262703365358872,
                            "ShowProbability": 0.15073604267248822
                        },
                        "7": {
                            "Umaban": "08",
                            "Enable": true,
                            "Wakuban": "5",
                            "WinProbability": 0.12327867029919387,
                            "ShowProbability": 0.3682785715176399
                        },
                        "8": {
                            "Umaban": "09",
                            "Enable": false,
                            "Wakuban": "5",
                            "WinProbability": 0.1238135656028967,
                            "ShowProbability": 0.13528497216830865
                        },
                        "9": {
                            "Umaban": "10",
                            "Enable": false,
                            "Wakuban": "6",
                            "WinProbability": 0.034296584883354665,
                            "ShowProbability": 0.08597085413707076
                        },
                        "10": {
                            "Umaban": "11",
                            "Enable": true,
                            "Wakuban": "6",
                            "WinProbability": 0.1086997597353546,
                            "ShowProbability": 0.39754199799747747
                        },
                        "11": {
                            "Umaban": "12",
                            "Enable": false,
                            "Wakuban": "7",
                            "WinProbability": 0.034507309464885096,
                            "ShowProbability": 0.07414846588753501
                        },
                        "12": {
                            "Umaban": "13",
                            "Enable": false,
                            "Wakuban": "7",
                            "WinProbability": 0.050792184209335976,
                            "ShowProbability": 0.1000619083106434
                        },
                        "13": {
                            "Umaban": "14",
                            "Enable": false,
                            "Wakuban": "8",
                            "WinProbability": 0.11740891979654182,
                            "ShowProbability": 0.18555582162756445
                        },
                        "14": {
                            "Umaban": "15",
                            "Enable": true,
                            "Wakuban": "8",
                            "WinProbability": 0.13867606237912863,
                            "ShowProbability": 0.34066133855697905
                        }
                    }
                }
            }
        }
    }
    """

    # JSONを読み込み
    json_data = json.loads(data_str)
    race_data = json_data["1201"]["06"]["03"]["uma"]

    # クラスをインスタンス化
    recommender = TrifectaRecommender(same_threshold=0.05)
    result = recommender.recommend_trifecta_bet(race_data)

    print("■ formation_type:", result.get("formation_type"))
    print("■ favorite:", result.get("favorite"))
    print("■ second_favorite:", result.get("second_favorite"))
    print("■ other:", result.get("other"))
    print("■ ticket_count:", result.get("ticket_count"))
    if "message" in result:
        print("■ message:", result["message"])
        print("■ message:", result["message"])
