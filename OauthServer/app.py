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
    'SECRET_KEY': 'secret',
    'OAUTH2_REFRESH_TOKEN_GENERATOR': True,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    # 'dockerserver': 'http://127.0.0.1:3476', # local
    # 'SQLALCHEMY_DATABASE_URI': 'sqlite:////tmp/db.sqlite', # local
    # 'logfile': './log', # local
    'myapik8s': 'http://myapi-k8s.default.svc.cluster.local:3476',
    # 'dockerserver': 'http://dockerserver:3476', # on docker
    'SQLALCHEMY_DATABASE_URI': 'sqlite:////app/OauthServer/db.sqlite', # on docker
    'logfile': '/app/OauthServer/log', # on docker
})


logger = logging.getLogger('oauthserver')
logger.debug('Start')

@app.cli.command()
def initdb():
    from oauthserver.models import db, add_user
    from oauthserver.box_models import db as boxdb, add_box, add_image
    logger.info("Recreate DataBase")
    db.drop_all()
    boxdb.drop_all()
    db.create_all()
    boxdb.create_all()
    db.session.commit()
    boxdb.session.commit()
    # testing
    add_user("test", 'test123', admin=1, quota=2)
    # add_box("test", 'testbox')
    add_image('user', 'nvidia/cuda:9.0-cudnn7-devel-ubuntu16.04', 'image_text')

@app.cli.command()
def std_add_user():
    from oauthserver.models import add_user
    from getpass import getpass
    import time
    name = input("Username ")
    passwd = getpass()
    passwd1 = getpass("Password Again: ")
    admin = int(input('Is admin (Y/n)') == 'Y')
    quota = int(input('Quota'))
    assert(passwd == passwd1 and len(passwd) >= 8)
    return add_user(name, passwd, time.time(), admin, quota)

@app.cli.command()
def std_add_box():
    from oauthserver.box_models import add_box
    user = input("Username ")
    box_name = input("box_name ")
    docker_name = input("docker_name ")
    node = input("node")
    image = input("image")
    add_box(user, docker_name, box_name, image, node)

@app.cli.command()
def std_add_image():
    from oauthserver.box_models import add_image
    user = input("Username ")
    name = input("Imagename ")
    description = input("description ")
    add_image(user, name, description)
