from csv_to_db_py.utils import cleaned_csv


def _write_csv(tmp_path, content):
    path = tmp_path / "data.csv"
    path.write_text(content)
    return str(path)


def test_detect_delimiter_not_called_when_delimiter_configured(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(
        cleaned_csv, "detect_delimiter", lambda p: calls.append(p) or ";"
    )
    df = cleaned_csv.get_dataframe_cleaned_new(
        _write_csv(tmp_path, "a,b\n1,2\n"), delimiter=","
    )
    assert calls == []
    assert df.columns == ["a", "b"]


def test_detect_delimiter_called_when_delimiter_absent(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(
        cleaned_csv, "detect_delimiter", lambda p: calls.append(p) or ";"
    )
    df = cleaned_csv.get_dataframe_cleaned_new(_write_csv(tmp_path, "a;b\n1;2\n"))
    assert calls == [str(tmp_path / "data.csv")]
    assert df.columns == ["a", "b"]
