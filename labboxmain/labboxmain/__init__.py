from .app import create_app
from config import config
import logging

app, celery = create_app(config)

# Before create box model, it need to create celery first
from .box import bp as boxbp, db as boxdb
app.register_blueprint(boxbp, url_prefix='/box/')
boxdb.init_app(app)

logger = logging.getLogger('labboxmain')
logger.info('[All] Start')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


@app.cli.command()
def initdb():
    from labboxmain.models import db, add_user
    from labboxmain.box_models import db as boxdb, add_image
    logger.warning('[Database] Recreate DataBase')
    db.drop_all()
    boxdb.drop_all()
    db.create_all()
    boxdb.create_all()
    db.session.commit()
    boxdb.session.commit()
    # testing
    add_user('linnil1', 'test123', groupid=1, quota=2)
    add_image('user', 'learn3.0', 'cuda9.0 cudnn7 python3')
    add_image('user', 'learn3.1', 'cuda9.0 cudnn7 python3 caffe2')


@app.cli.command()
def std_add_user():
    from labboxmain.models import add_user
    from getpass import getpass
    import time
    name = input('Username ')
    passwd = getpass()
    passwd1 = getpass('Password Again: ')
    groupid = int(input('Group: (Interger)'))
    quota = int(input('Quota: '))
    assert(passwd == passwd1 and len(passwd) >= 8)
    return add_user(name, passwd, time.time(), groupid, quota)


@app.cli.command()
def std_add_image():
    from labboxmain.box_models import add_image
    user = input('Username ')
    name = input('Imagename ')
    description = input('description ')
    add_image(user, name, description)
