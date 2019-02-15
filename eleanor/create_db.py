from eleanor.db import db
from eleanor.eleanor import create_app

try:
    from eleanor.settings import DROP_BEFORE_CREATE
except ImportError:
    from eleanor.default_settings import DROP_BEFORE_CREATE


app = create_app()
db.init_app(app)
with app.app_context():
    if DROP_BEFORE_CREATE:
        db.drop_all()
        db.create_all()
    db.create_all()
