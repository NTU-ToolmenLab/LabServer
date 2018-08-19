from oauthserver.app import create_app
import logging

app = create_app({
    'bullet': """
<p> <a href="/passwd">   Change Your Password </a></p>
<p> <a href="/drive/">   NextCloud Drive      </a></p>
<p> <a href="/monitor/"> Monitor Web          </a></p>
<p> <a href="/help">     Help Web             </a></p>
""",
    'name': 'Lab304',
    # 'dockerserver': 'http://dockerserver:3476', # on docker
    'dockerserver': 'http://127.0.0.1:3476',
    'SECRET_KEY': 'secret',
    'OAUTH2_REFRESH_TOKEN_GENERATOR': True,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:////tmp/db.sqlite',
    # 'SQLALCHEMY_DATABASE_URI': 'sqlite:////app/OauthServer/db.sqlite', # on docker
    # 'logfile': '/app/OauthServer/log', # on docker
    'logfile': './log',
})


logger = logging.getLogger('oauthserver')
logger.debug('Start')

@app.cli.command()
def initdb():
    from oauthserver.models import db, add_user
    from oauthserver.box import db as boxdb, add_box
    logger.info("Recreate DataBase")
    db.drop_all()
    boxdb.drop_all()
    db.create_all()
    boxdb.create_all()
    db.session.commit()
    boxdb.session.commit()
    # testing
    # add_user("test", 'test123', admin=1)
    # add_user("test_user", 'test123123')
    # add_box("test", 'testbox')

@app.cli.command()
def std_add_user():
    from oauthserver.models import add_user
    name = input("Username ")
    passwd = getpass()
    passwd1 = getpass("Password Again: ")
    admin = int(input('Is admin (Y/n)') == 'Y')
    assert(passwd == passwd1 and len(passwd) >= 8)
    return add_user(name, passwd, time.time(), admin)

@app.cli.command()
def std_add_box():
    from oauthserver.box import add_box
    user = input("Username ")
    box_name = input("box_name ")
    docker_name = input("docker_name ")
    add_box(user, docker_name, box_name)
