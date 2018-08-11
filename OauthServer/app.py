from oauthserver.app import create_app

app = create_app({
    'SECRET_KEY': 'secret',
    'OAUTH2_REFRESH_TOKEN_GENERATOR': True,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:////tmp/db.sqlite',
})


@app.cli.command()
def initdb():
    from oauthserver.models import db, User
    import passlib.hash
    db.drop_all()
    db.create_all()
    p = passlib.hash.sha512_crypt.hash('test123')
    user = User(name="test", password=p, admin=0)
    db.session.add(user)
    db.session.commit()
