from datum.config import APP_DATA_DIR, Settings


def test_default_chain_path():
    settings = Settings()
    expected_path = APP_DATA_DIR / "ledger.json"
    assert settings.chain_file == str(expected_path)

def test_config_dir_creation():
    assert APP_DATA_DIR.exists()
    assert APP_DATA_DIR.is_dir()
