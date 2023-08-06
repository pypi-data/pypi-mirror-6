"""
    fabfile

    Fabric script to deploy nereid-webshop to demo

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import os
import getpass

import requests
from fabric.tasks import execute
from fabric.api import sudo, cd, prefix, run, env
from fabric.decorators import hosts

# Forward the SSH agent so that git pull works
env.forward_agent = True
env.use_ssh_config = True

hipchat_notification_token = open(
    os.path.expanduser('~/.hipchat-token')
).read().replace('\n', '')


def notify_hipchat(
        message, from_='deployer', color='gray', room_id='384754',
        message_format="text", notify=False):
    """
    Send the given message to hipchat room
    """
    rv = requests.post(
        "https://api.hipchat.com/v1/rooms/message?format=json"
        "&auth_token=%s" % (hipchat_notification_token),
        data={
            'room_id': room_id,
            'from': '%s [%s]' % (from_, env.user),
            'message': '[%s] %s' % (env.host, message),
            'message_format': message_format,
            'notify': notify and 1 or 0,
            'color': color,
        }
    )
    return rv


def _update_schema(database, module=None):
    "Run trytond and update schema for given database"
    if module:
        run(
            'trytond -c etc/trytond.conf -u %s -d %s' % (
                module, database
            )
        )
    else:
        run('trytond -c etc/trytond.conf -u nereid_webshop -d %s' % database)


@hosts('%s@nereid-webshop-demo.openlabs.us' % getpass.getuser())
def deploy_staging(schema_update=False):
    "Deploy to staging"
    notify_hipchat("Beginning deployment")
    root_path = '/opt/webshop_demo'
    sudo('chmod -R g+rw %s' % root_path)

    with prefix("source %s/bin/activate" % root_path):
        with cd(root_path):
            for module in ('nereid-webshop', ):
                with cd(module):
                    run('git fetch')
                    run('git checkout origin/develop')
                    run('python setup.py install')

            if schema_update:
                execute(_update_schema, 'webshop_demo')

            notify_hipchat("Restarting services")
            run('supervisorctl restart all')


@hosts('%s@nereid-webshop-demo.openlabs.us' % getpass.getuser())
def update_module(module, tag_or_branch='origin/develop'):
    "Deploy to staging"
    notify_hipchat("Updating module %s" % module)
    root_path = '/opt/webshop_demo'
    sudo('chmod -R g+rw %s' % root_path)

    with prefix("source %s/bin/activate" % root_path):
        with cd(root_path):
            with cd(module):
                run('git fetch')
                run('git checkout %s' % tag_or_branch)
            run('pip install %s/' % module)

            execute(_update_schema, 'webshop_demo', module.replace('-', '_'))

            notify_hipchat("Restarting services")
            run('supervisorctl restart all')
