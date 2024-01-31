from typing import Any, Dict, List

import pandas as pd


class HorsePillar:
    _jyo_cd_to_jyo = {
        "01": "札幌",
        "02": "函館",
        "03": "福島",
        "04": "新潟",
        "05": "東京",
        "06": "中山",
        "07": "中京",
        "08": "京都",
        "09": "阪神",
        "10": "小倉",
    }

    def __init__(
        self, json: Dict[str, Dict[str, Dict[str, Dict[str, List[Dict[str, Any]]]]]]
    ):
        self._json_horse_pillar = json
        self._year = list(self._json_horse_pillar.keys())[0]
        self._monthday = list(self._json_horse_pillar[self._year].keys())[0]
        self._jyo = list(self._json_horse_pillar[self._year][self._monthday].keys())[0]
        self._race_num = list(
            self._json_horse_pillar[self._year][self._monthday][self._jyo].keys()
        )[0]

    def get_horse_pillar(self) -> pd.DataFrame:
        """該当レースの馬柱を返す

        Returns:
            pd.DataFrame: 馬柱
        """
        if self._has_horse_pillar():
            return self._json_horse_pillar[self._year][self._monthday][self._jyo][
                self._race_num
            ]
        else:
            return {}

    def _correct_invalid_key(self, key: str, list: List[str]):
        if key in list:
            return key
        else:
            return list[0]

    def set_race(self, year, monthday, jyo, race_num):
        self._year = year
        self._year = self._correct_invalid_key(year, self.year_list)
        self._monthday = monthday
        self._monthday = self._correct_invalid_key(monthday, self.monthday_list)
        self._jyo = jyo
        self._jyo = self._correct_invalid_key(jyo, self.jyo_list)
        self._race_num = race_num
        self._race_num = self._correct_invalid_key(race_num, self.race_num_list)

        print("set", self._year, self._monthday, self._jyo, self._race_num)

    def _has_horse_pillar(self) -> bool:
        """年、月日、競馬場、レース番号の馬柱がある場合Trueを返す

        Returns:
            bool: 年、月日、競馬場、レース番号の馬柱があればTrue
        """
        if self._year in self.year_list:
            if self._monthday in self.monthday_list:
                if self._jyo in self.jyo_list:
                    if self._race_num in self.race_num_list:
                        return True

        return False

    @property
    def year(self):
        return self._year

    @property
    def monthday(self):
        return self._monthday

    @property
    def jyo(self):
        return self._jyo

    @property
    def race_num(self):
        return self._race_num

    @property
    def year_list(self):
        return list(self._json_horse_pillar.keys())

    @property
    def monthday_list(self):
        return list(self._json_horse_pillar[self._year].keys())

    @property
    def jyo_list(self):
        return list(self._json_horse_pillar[self._year][self._monthday].keys())

    @property
    def race_num_list(self):
        return list(
            self._json_horse_pillar[self._year][self._monthday][self._jyo].keys()
        )
