import os

from django.core.management.utils import get_random_secret_key
from fabric.api import cd
from fabric.api import env
from fabric.api import local
from fabric.api import run
from fabric.contrib.files import append
from fabric.contrib.files import exists

REPO_URL = 'https://github.com/jhryan/tdd-web-dev.git'


def deploy():
    site_folder = f'/home/{env.user}/sites/{env.host}'
    run(f'mkdir -p {site_folder}')
    with cd(site_folder):
        _get_latest_source()
        _update_virtualenv()
        _create_or_update_dotenv()
        _update_static_files()
        _update_database()


def _get_latest_source():
    if exists('.git'):
        run('git fetch')
    else:
        run(f'git clone {REPO_URL} .')
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run(f'git reset --hard {current_commit}')


def _update_virtualenv():
    if not exists('virtualenv/bin/pip'):
        run(f'python3.6 -m venv virtualenv')
    run('./virtualenv/bin/pip install -r requirements.txt')


def _create_or_update_dotenv():
    append('.env', 'DJANGO_DEBUG_FALSE=y')
    append('.env', f'SITENAME={env.host}')
    current_contents = run('cat .env')
    if 'DJANGO_SECRET_KEY' not in current_contents:
        new_secret = get_random_secret_key()
        append('.env', f"DJANGO_SECRET_KEY='{new_secret}'")
    email = os.environ['EMAIL']
    append('.env', f'EMAIL={email}')
    email_password = os.environ['EMAIL_PASSWORD']
    append('.env', f'EMAIL_PASSWORD={email_password}')


def _update_static_files():
    run('./virtualenv/bin/python manage.py collectstatic --noinput')


def _update_database():
    run('./virtualenv/bin/python manage.py migrate --noinput')
