import json
from typing import Any, Dict


class RaceReader:
    @classmethod
    def read(cls, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, "r", encoding="utf_8") as f:
                return json.load(f)
        except FileNotFoundError:
            return "ファイルが見つかりません。"
        except json.JSONDecodeError:
            return "無効なJSONファイルです。"
        except Exception as e:
            return f"予期せぬエラーが発生しました: {e}"
