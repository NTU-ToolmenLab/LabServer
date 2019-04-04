from celery.schedules import crontab

config = {
    'bullet': """
<p> <a href="/passwd">   Change Your Password </a></p>
<p> <a href="/drive/">   NextCloud Drive      </a></p>
<p> <a href="/monitor/"> Monitor Web          </a></p>
<p> <a href="/help">     Help Web             </a></p>
""",
    'name': 'Lab304',
    'SECRET_KEY': '{{ secretkey }}',
    'OAUTH2_REFRESH_TOKEN_GENERATOR': True,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    # 'dockerserver': 'http://127.0.0.1:3476',               # local
    # 'SQLALCHEMY_DATABASE_URI': 'sqlite:////tmp/db.sqlite', # local
    # 'logfile': './log',                                    # local
    # 'dockerserver': 'http://dockerserver:3476', # Use without kubernetes
    'myapik8s': 'http://myapi-k8s.default.svc.cluster.local:3476', # Use without dockercompose
    'SQLALCHEMY_DATABASE_URI': 'sqlite:////app/OauthServer/db.sqlite',
    'logfile': '/app/OauthServer/log',
    'sshpiper': '/app/sshpiper/',
    # 'registry_url': 'server:5000',           # can be empty string
    'registry_url': 'harbor.default.svc.cluster.local',      # can be empty string
    'registry_user': 'user',                   # optinoal when you need private registry
    'registry_password': '{{ registry_password }}',           # optinoal when you need private registry
    'registry_backup': 'user/backup',
    'registry_images': 'linnil1/serverbox',
    'celery_broker_url': 'redis://box-redis.default.svc.cluster.local:6379',
    'celery_result_backend': 'redis://box-redis.default.svc.cluster.local:6379',
    'celery_schedule': {'commit-every-day': {
        'task': 'oauthserver.box.goCommit',
            'schedule': crontab(hour=2, minute=0),
        }
    }
}
