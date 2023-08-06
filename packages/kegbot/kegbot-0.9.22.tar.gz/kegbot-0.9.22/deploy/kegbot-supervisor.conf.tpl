# Supervisor configuration for Kegbot server.
#
# Instructions:
#   - Replace "/data/kegbot/kb/bin" with the installed path of the kegbot
#     programs.
#   - Replace "user=ubuntu" with the username you wish to run the programs.
#   - Edit paths.
#   - Copy to /etc/supervisor/conf.d/kegbot.conf

[group:kegbot]
programs=gunicorn,celery,celerybeat

[program:gunicorn]
command=${kegbot_bin} run_gunicorn --settings=pykeg.settings -w 3
directory=${kegbot_root}
user=${user}
autostart=true
autorestart=true
redirect_stderr=true

[program:celery]
command=${celery_bin} -A pykeg multi start default stats -c:default 3 -c:stats 1 -Q:default default -Q:stats stats
directory=${kegbot_root}
user=${user}
autostart=true
autorestart=true
redirect_stderr=true

[program:celerybeat]
command=${celery_bin} -A pykeg beat -l info
directory=${kegbot_root}
user=${user}
autostart=true
autorestart=true
redirect_stderr=true

