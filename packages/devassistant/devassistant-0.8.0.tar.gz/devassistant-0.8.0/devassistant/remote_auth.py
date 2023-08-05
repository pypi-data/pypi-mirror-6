import getpass
import os

from devassistant import exceptions
from devassistant import settings
from devassistant import utils
from devassistant.command_helpers import ClHelper, DialogHelper
from devassistant.logger import logger

class GitHubAuth(object):
    _user = None
    _token = None
    try:
        _gh_module = utils.import_module('github')
    except:
        _gh_module = None

    @classmethod
    def _github_token(cls, login):
        if not cls._token:
            try:
                cls._token = ClHelper.run_command("git config github.token.{login}".format(
                    login=login))
            except exceptions.ClException:
                pass # token is not available yet

        return cls._token

    @classmethod
    def _get_github_user(cls, login):
        if not cls._user:
            try:
                # try logging with token
                token = cls._github_token(login)
                gh = cls._gh_module.Github(login_or_token=token)
                cls._user = gh.get_user()
                # try if the authentication was successful
                cls._user.login
            except cls._gh_module.GithubException:
                # if the token was set, it was wrong, so make sure it's reset
                cls._token = None
                # login with username/password
                password = DialogHelper.ask_for_password(
                        prompt='Github Password for {username}:'.format(username=login))
                gh = cls._gh_module.Github(login_or_token=login, password=password)
                cls._user = gh.get_user()
                try:
                    cls._user.login
                    cls._github_create_auth() # create auth for future use
                except cls._gh_module.GithubException as e:
                    msg = 'Wrong username or password\nGitHub exception: {0}'.format(e)
                    # reset cls._user to None, so that we don't use it if calling this multiple times
                    cls._user = None
                    raise exceptions.CommandException(msg)
        return cls._user

    @classmethod
    def _github_create_auth(cls):
        """ Store token into ~/.gitconfig.

        If token is not defined then store it into ~/.gitconfig file
        """
        if not cls._token:
            try:
                auth = cls._user.create_authorization(scopes=['repo', 'user'], note="DeveloperAssistant")
                ClHelper.run_command("git config --global github.token.{login} {token}".format(
                    login=cls._user.login,
                    token=auth.token))
                ClHelper.run_command("git config --global github.user.{login} {login}".format(
                    login=cls._user.login))
            except cls._gh_module.GithubException as e:
                logger.warning('Creating authorization failed: {0}'.format(e))

    @classmethod
    def _github_create_ssh_key(cls):
        try:
            login = cls._user.login
            pkey_path = '{home}/.ssh/{keyname}'.format(home=os.path.expanduser('~'),
                                                       keyname=settings.GITHUB_SSH_KEYNAME.format(login=login))
            # create ssh keys here
            if not os.path.isfile('{pkey_path}.pub'.format(pkey_path=pkey_path)):
                ClHelper.run_command('ssh-keygen -t rsa -f {pkey_path}\
                                     -N \"\" -C \"DeveloperAssistant\"'.\
                                     format(pkey_path=pkey_path))
                ClHelper.run_command('ssh-add {pkey_path}'.format(pkey_path=pkey_path))
            public_key = ClHelper.run_command('cat {pkey_path}.pub'.format(pkey_path=pkey_path))
            # find out if this key is already registered with this user
            for key in cls._user.get_keys():
                # don't use "==" because we have comments etc added in public_key
                if key._key in public_key:
                    break
            else:
                cls._user.create_key("devassistant", public_key)
            # next, create ~/.ssh/config entry for the key, if system username != GH login
            cls._github_create_ssh_config_entry()
        except exceptions.ClException:
            pass # TODO: determine and log the error

    @classmethod
    def _github_create_ssh_config_entry(cls):
        if getpass.getuser() != cls._user.login:
            ssh_config = os.path.expanduser('~/.ssh/config')
            user_github_string = 'github.com-{0}'.format(cls._user.login)
            needs_to_add_config_entry = True

            if os.path.isfile(ssh_config):
                fh = open(ssh_config)
                config_content = fh.read()
                if user_github_string in config_content:
                    needs_to_add_config_entry = False
                fh.close()
            if needs_to_add_config_entry:
                fh = os.fdopen(os.open(ssh_config, os.O_WRONLY|os.O_CREAT|os.O_APPEND, 0o600), 'a')
                fh.write(settings.GITHUB_SSH_CONFIG.format(
                            login=cls._user.login,
                            keyname=settings.GITHUB_SSH_KEYNAME.format(login=cls._user.login)))
                fh.close()

    @classmethod
    def github_authenticated(cls, func):
        """Does user authentication, creates SSH keys if needed and injects "_user" attribute
        into class/object bound to the decorated function.
        Don't call any other methods of this class manually, this should be everything you need.
        """
        def inner(func_cls, *args, **kwargs):
            if not cls._gh_module:
                logger.warning('PyGithub not installed, skipping github authentication procedures.')
            elif not func_cls._user:
                # authenticate user, possibly also creating authentication for future use
                func_cls._user = cls._get_github_user(kwargs['login'])
                # create ssh key for pushing
                cls._github_create_ssh_key()
            return func(func_cls, *args, **kwargs)

        return inner
