# coding=utf8

import os
import string

from fabric.operations import run, local

from fuzzy_fabric.functils import *


# --- Variables ---

def get_var(var_name=None):
    if not os.path.isfile('fabric.ini'):
        return None if var_name else {}

    from ConfigParser import SafeConfigParser

    config_parser = SafeConfigParser()
    config_parser.read('fabric.ini')

    if var_name:
        return config_parser.get('main', var_name)
    else:
        return dict(config_parser.items('main'))

# --- Init ---

def copy_and_fill(file_path, ensure_name=False, **kwargs):
    """
    Copy file from templates to project and substitute variables
    """
    if os.path.isfile(file_path):
        warning("'{}' exists already", file_path)
        if confirm("Rewrite '{}'?", file_path):
            os.remove(file_path)
        else:
            return None

    vars = get_var()
    vars.update(kwargs)

    if 'name' not in vars and ensure_name:
        vars['name'] = ensure_prompt('Project name:')

    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    template_path = os.path.join(templates_dir, file_path)
    template_string = open(template_path).read().decode('utf8')

    template = string.Template(template_string)
    content = template.safe_substitute(vars)

    open(file_path, 'w').write(content)

    if os.path.isfile(file_path):
        success("'{}' was wrote", file_path)
    else:
        error("'{}' is not exists", file_path)


def init_setup():
    """
    setup.py
    """
    copy_and_fill('setup.py', ensure_name=True)


def init_readme():
    """
    README.rst
    """
    copy_and_fill('README.rst')


def init_fabric():
    """
    fabric.ini
    """
    copy_and_fill('fabric.ini', ensure_name=True)


def init_hgignore():
    """
    .hgignore
    """
    return copy_and_fill('.hgignore')


def init_gitignore():
    """
    .gitignore
    """
    return copy_and_fill('.gitignore')


def init_nginx():
    """
    nginx
    """
    pass


@task
def init():
    """
    setup.py/README.rst/fabric.ini/...
    """
    functions = [
        init_setup,
        init_readme,
        init_fabric,
        init_gitignore,
        init_hgignore,
    ]
    return call_choosen(functions, 'Init')


# -----------------------------------------------


# --- project ---
def project_init():
    project_name = prompt('Project name: ')

    if not project_name:
        return

    env_init()
    if environment.confirm('Install Django?'):
        install('django')
        environment.env('python django-admin.py startproject ' + project_name)

    project_init_copy()
    repo_init()
    addremove()
    commit()
    push()


def hg_addremove():
    environment('hg addremove --dry-run')
    if environment.confirm("hg addremove ?"):
        if environment('hg addremove').succeeded:
            environment.success('hg addremove SUCCESS')
        else:
            environment.error('hg addremove FAIL')


# --- setuptools ---
@task
def upload():
    """
    setup.py sdist upload
    """
    environment('python setup.py sdist upload')


# --- Deploy ---
@task
def pd():
    """
    prepare & deploy
    """
    prepare()
    deploy()


@task
def prepare():
    """
    prepare for deploy
    """
    if environment.package:
        package_prepare()
    else:
        project_prepare()


def project_prepare():
    # splitreqs()
    # addremove()
    commit()
    push()


def project_deploy():
    remote()
    pull()
    update()
    # pip_update_requirements('no-deps')
    collectstatic()
    restart()

# =================================================
@task
def ls():
    environment('ls')


def stop():
    fabric.operations

@task
def p(package):
    global environment
    # environment.package = True
    environment.info("swith to {}", package)
    if package in environment.packages:
        environment = environment.packages[package]
        environment.success('Switched to {name}')
        environment.package = True
    else:
        # environment.error("No package '{}'", package)
        fabric.utils.abort(red("No package '{}'".format(package)))


def package_prepare():
    branch = environment('hg branch', capture=True)
    print red(branch)
    if not environment.confirm("Commit to '{branch}'?", branch=branch):
        return
    # if not package.is_dev_branch(branch):
    #     return environment.error("Чтобы продолжить должна быть выбрана ветка sdev. Сейчас выбрана '{}'", branch)
    addremove()
    commit()
    update(environment.stable_branch)
    merge(branch)
    commit('merge ' + branch)
    update(branch)
    push()


def package_deploy(package):
    remote()
    pull()
    update(environment.stable_branch)


def merge(branch=''):
    environment('hg merge ' + branch)


@task
def deploy():
    """
    [project/nginx/wsgi] deploy
    """
    if environment.package:
        return package_deploy()

    if environment.nginx:
        nginx_deploy()
    elif environment.wsgi:
        wsgi_deploy()
    else:
        project_deploy()


def hg_pull():
    if environment('hg pull {hg_path}').succeeded:
        environment.success('hg pull SUCCESS')
    else:
        environment.error('hg pull FAIL')


def hg_update(branch=''):
    if environment('hg update ' + branch).succeeded:
        environment.success("Updated on '{branch}'", branch=branch)
    else:
        environment.error('Update failed')


@task
def update(branch=''):
    """
    [hg/git] update
    """
    if environment.hg:
        hg_update(branch=branch)
    elif environment.git:
        git_update()
    else:
        environment.error('Update failed. No repo.')


def hg_push():
    if environment('hg push {hg_path}').successed:
        environment.success('Pushed')
    else:
        # todo не работает
        environment.error('Push failed')


def git_push():
    if environment('git-push {git_path}'):
        environment.error('Pushed')
    else:
        environment.success('Push failed')


@task
def push():
    """
    [hg/git] push
    """
    if environment.hg:
        hg_push()
    elif environment.git:
        git_push()


def nginx_deploy():
    raise NotImplementedError
    # fabric.api.put(dev.root.config.nginx, '/etc/nginx/sites-enabled/')


def wsgi_deploy():
    raise NotImplementedError
    # fabric.api.put(dev.root.config.uwsgi, '/etc/uwsgi/apps-enabled/')


# --- manage.py ---
@task
def manage(command):
    """
    manage.py [...]
    """
    environment.env('./manage.py ' + command)


@task
def collectstatic():
    """
    manage.py collectstatic --noinput
    """
    environment.env('python manage.py collectstatic --noinput')
    environment.success('Static collected')


@task
def migrate(app_name):
    """
    [fake] manage.py migrate [...]
    """
    params = '--fake ' if environment.fake else ''
    environment.env('./manage.py ' + params + app_name)


def hg_commit(message=''):
    if not message:
        message = environment.prompt('Commit message:')

    if message:
        if environment('hg commit -m "{message}"', message=message).succeeded:
            environment.success('Commited')
    else:
        environment.error('Commit failed')


@task
def commit(message=''):
    """
    [hg/git] commit
    """
    if environment.hg:
        hg_commit(message=message)
    elif environment.git:
        git_commit(message=message)
    else:
        environment.error('Commit failed. No repo.')


@task
def schemamigration(app_name):
    """
    manage.py schemamigration --auto [...]
    """
    environment.env('./manage.py schemamigration --auto ' + app_name)


@task
def remote():
    """
    remote [any command]
    """
    environment.remote = True


@task
def restart():
    """
    restart remote server (uWSGI restart)
    """
    remote()
    environment('/etc/init.d/uwsgi restart')


@task
def shell():
    """
    fabric.operations.open_shell()
    """
    fabric.operations.open_shell()

