# vim: tabstop=4 shiftwidth=4 softtabstop=4
import fabtools.files
import fabtools.require


from fabric.api import execute
from fabric.api import parallel
from fabric.api import roles
from fabric.api import sudo
from farmboy.fabric_ import task


# http://thegunicorn.com/


@task
@roles('web')
def deploy():
    """Add gunicorn to the <web> hosts."""
    fabtools.require.deb.packages([
        'gunicorn'
    ])
    restart()


#@task
#@roles('web')
def restart():
    """Gunicorn doesn't act super swell, so look for a PID."""
    sudo('service gunicorn restart', pty=False)
    #if fabtools.files.is_file('/var/run/gunicorn/django.pid'):
    #    sudo('service gunicorn restart', pty=False)
    #else:
    #    #fabtools.service.start('gunicorn')
    #    sudo('service gunicorn start', pty=False)
