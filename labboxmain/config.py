from celery.schedules import crontab


# groupid=1 -> admin
# groupid=0 -> Our users
# groupid=2 -> Other users
# groupid=3 -> Our guest
def create_rule(user):
    create_param = {}
    if user.groupid <= 1:
        create_param.update({
            'homepvc': "nfs-homenas",
            'naspvc': "nfs-labnas",
        })
    if user.groupid == 2:
        create_param.update({
            'homepath': 'sfc/' + user.name,
            'homepvc': "nfs-homenas",
            'naspvc': "",
            'node': 'lab304-server3'
        })
    elif user.groupid == 3:
        create_param.update({
            'homepath': 'summer/' + user.name,
            'homepvc': "nfs-homenas",
            'naspvc': "",
        })
    return create_param


config = {
    # basic
    'bullet': "",
    'name': 'Toolmen',
    'domain_name': '{{ domain_name }}',
    'SECRET_KEY': '{{ secretkey }}',
    'OAUTH2_REFRESH_TOKEN_GENERATOR': True,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:////app/db.sqlite',
    'SCHEDULER_API_ENABLED': True,
    'logfile': '/app/log',
    'create_rule': create_rule,

    # Method for connecting to pod
    'sshpiper': '/app/sshpiper/',
    'vnc_password': '{{ vncpw }}',

    # API: k8s + docker or docker only
    # 'labboxapi-docker': 'http://dockerserver:3476', # Use without kubernetes
    'labboxapi-k8s': 'http://labboxapi-k8s.default.svc.cluster.local:3476', # Use without dockercompose

    # Registry settigs
    'registry_url': 'harbor.default.svc.cluster.local', # empty to disable
    'registry_user': 'user',
    'registry_password': '{{ registry_password }}',
    'registry_repo_backup': 'user/backup',
    'registry_repo_default': 'linnil1/serverbox',

    # Backgroud method
    'celery_broker_url': 'redis://labboxdb-redis.default.svc.cluster.local:6379',
    'celery_result_backend': 'redis://labboxdb-redis.default.svc.cluster.local:6379',
    'celery_schedule': {
        'box-routine': {
            'task': 'labboxmain.box.routineMaintain',
            'schedule': crontab(hour=2, minute=0),
        },
        'queue-run': {
            'task': 'labboxmain.box_queue.scheduleGPU',
            'schedule': crontab(minute='*'),
        },
    },

    # GPU settings
    'gpu_monitor_url': 'http://lab-monitor-prometheus-server.monitor.svc.cluster.local/api/v1/',
    'gpu_query_metrics': ['nvidia_gpu_duty_cycle', 'nvidia_gpu_memory_used_bytes / nvidia_gpu_memory_total_bytes'],
    'gpu_query_interval': 60,
    'gpu_exe_interval': 120,
}
