import os

if not os.environ.get("SECRET_KEY"):
    _key_path = os.path.join(
        os.environ.get("DATA_DIR", "/app/data"), ".flask_secret_key"
    )
    try:
        with open(_key_path) as f:
            _key = f.read().strip()
        if _key:
            os.environ["SECRET_KEY"] = _key
    except FileNotFoundError:
        pass
    if not os.environ.get("SECRET_KEY"):
        _key = os.urandom(32).hex()
        os.environ["SECRET_KEY"] = _key
        try:
            os.makedirs(os.path.dirname(_key_path), exist_ok=True)
            with open(_key_path, "w") as f:
                f.write(_key)
        except OSError:
            pass

from app import create_app

app = create_app()
