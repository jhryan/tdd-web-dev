from fabric.api import run
from fabric.context_managers import settings
from fabric.context_managers import shell_env


def _get_manage_dot_py(host):
    return f'~/sites/{host}/virtualenv/bin/python ~/sites/{host}/manage.py'


def reset_database(host):
    manage_dot_py = _get_manage_dot_py(host)
    with settings(host_string=f'john@{host}'):
        run(f'{manage_dot_py} flush --noinput')


def _get_server_env_vars(host):
    env_lines = run(f'cat ~/sites/{host}/.env').splitlines()
    env_dict = dict(l.split('=', 1) for l in env_lines if l)
    for key, val in env_dict.items():
        env_dict[key] = val.strip("'")
    return env_dict


def create_session_on_server(host, email):
    manage_dot_py = _get_manage_dot_py(host)
    with settings(host_string=f'john@{host}'):
        env_vars = _get_server_env_vars(host)
        with shell_env(**env_vars):
            session_key = run(f'{manage_dot_py} create_session {email}')
            return session_key.strip()
