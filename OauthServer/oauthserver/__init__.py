from .app import create_app
from config import config
import logging

app, celery = create_app(config)

# Before create box model, it need to create celery first
from .box import bp as boxbp, db as boxdb
app.register_blueprint(boxbp, url_prefix='/box/')
boxdb.init_app(app)

logger = logging.getLogger('oauthserver')
logger.debug('Start')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


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
    add_user("linnil1", 'test123', groupid=1, quota=2)
    # add_box("test", 'testbox')
    add_image('user', 'learn3.0', 'cuda9.0 cudnn7 python3 tensorflow1.11 keras2.2.4 pytorch0.4.1')
    add_image('user', 'learn3.1', 'cuda9.0 cudnn7 python3 caffe2')


@app.cli.command()
def std_add_user():
    from oauthserver.models import add_user
    from getpass import getpass
    import time
    name = input("Username ")
    passwd = getpass()
    passwd1 = getpass("Password Again: ")
    groupid = int(input('Group: (Interger)'))
    quota = int(input('Quota: '))
    assert(passwd == passwd1 and len(passwd) >= 8)
    return add_user(name, passwd, time.time(), groupid, quota)


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
