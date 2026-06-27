from pathlib import Path

from sv_generator.openapi_loader import load_openapi


def test_load_openapi_success(tmp_path: Path) -> None:
    yaml_file = tmp_path / 'eligibility.yaml'
    yaml_file.write_text("""openapi: 3.0.3
paths: {}
""", encoding='utf-8')
    document = load_openapi(yaml_file)
    assert document['openapi'] == '3.0.3'


def test_load_openapi_missing_paths(tmp_path: Path) -> None:
    yaml_file = tmp_path / 'invalid.yaml'
    yaml_file.write_text("""openapi: 3.0.3
""", encoding='utf-8')
    try:
        load_openapi(yaml_file)
        assert False, 'Expected ValueError for missing paths'
    except ValueError as exc:
        assert 'paths' in str(exc)
