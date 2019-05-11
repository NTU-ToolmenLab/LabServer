from celery.schedules import crontab

config = {
    'bullet': """
""",
    'name': 'Lab304',
    'domain_name': 'my.domain.ntu.edu.tw',
    'SECRET_KEY': '{{ secretkey }}',
    'OAUTH2_REFRESH_TOKEN_GENERATOR': True,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    # 'dockerserver': 'http://127.0.0.1:3476',               # local
    # 'SQLALCHEMY_DATABASE_URI': 'sqlite:////tmp/db.sqlite', # local
    # 'logfile': './log',                                    # local
    # 'dockerserver': 'http://dockerserver:3476', # Use without kubernetes
    'myapik8s': 'http://labboxapi-k8s.default.svc.cluster.local:3476', # Use without dockercompose
    'SQLALCHEMY_DATABASE_URI': 'sqlite:////app/db.sqlite',
    'logfile': '/app/log',
    'sshpiper': '/app/sshpiper/',
    # 'registry_url': 'server:5000',           # can be empty string
    'registry_url': 'harbor.default.svc.cluster.local',      # can be empty string
    'registry_user': 'user',                   # optinoal when you need private registry
    'registry_password': '{{ registry_password }}',           # optinoal when you need private registry
    'registry_backup': 'user/backup',
    'registry_images': 'linnil1/serverbox',
    'celery_broker_url': 'redis://labboxdb-redis.default.svc.cluster.local:6379',
    'celery_result_backend': 'redis://labboxdb-redis.default.svc.cluster.local:6379',
    'celery_schedule': {
        'box-routine': {
            'task': 'labboxmain.box.routineMaintain',
            'schedule': crontab(hour=18, minute=0),
        },
    }
}
