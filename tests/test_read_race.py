import json

import pytest

from src.read_race import RaceReader


def test_read_json_file_valid(mocker):
    # 期待されるJSONデータ
    expected_data = {"key": "value"}

    # open関数のモックを作成
    mocker.patch("builtins.open", mocker.mock_open(read_data=json.dumps(expected_data)))

    # json.loadのモックを作成
    mocker.patch("json.load", return_value=expected_data)

    # 正常なファイルの読み込みをテスト
    assert RaceReader.read("valid_path.json") == expected_data


def test_read_json_file_not_found(mocker):
    # ファイルが存在しない場合のテスト
    mocker.patch("builtins.open", side_effect=FileNotFoundError)

    assert RaceReader.read("invalid_path.json") == "ファイルが見つかりません。"


def test_read_json_file_invalid_json(mocker):
    # JSONのフォーマットが無効な場合のテスト
    mocker.patch("builtins.open", mocker.mock_open(read_data="invalid json"))
    mocker.patch(
        "json.load", side_effect=json.JSONDecodeError("Expecting value", "", 0)
    )

    assert RaceReader.read("invalid_json.json") == "無効なJSONファイルです。"
