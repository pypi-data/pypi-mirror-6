#!/usr/bin/env python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# Author: "Chris Ward" <cward@redhat.com>

''' "Metrique User Management" related funtions '''

import os

from metriqueu.utils import set_default


def aboutme(self, username=None):
    '''
    Get user profile details

    :param string username: username to query profile data for
    '''
    username = set_default(username, self.config.username)

    cmd = os.path.join(username, 'aboutme')
    result = self._get(cmd, api_url=False)
    return result


def register(self, username=None, password=None, logon_as=True):
    '''
    Register new user

    :param String user: Name of the user you're managing
    :param String password: Password (plain text), if any of user
    '''
    username = set_default(username, self.config.username)
    password = set_default(password, self.config.password)
    result = self._post('register',
                        username=username, password=password,
                        api_url=False)
    if result and logon_as:
        # start a fresh session (empty cookiesjar), with the
        # new registered users
        self.config['username'] = username
        self.config['password'] = password
        return login(self, username, password)
    else:
        return result


def remove(self, username=None, quiet=False):
    '''
    Remove existing user

    :param String username: Name of the user you're managing
    :param bool quiet: ignore exceptions
    '''
    username = set_default(username, self.config.username)
    cmd = os.path.join(username, 'remove')
    try:
        result = self._delete(cmd, username=username, api_url=False)
    except Exception:
        if quiet:
            result = None
        else:
            raise
    return result


def login(self, username=None, password=None):
    '''
    Login a user

    :param String user: Name of the user you're managing
    :param String password: Password (plain text), if any of user
    '''
    username = set_default(username, self.config.username,
                           err_msg='username required')
    password = set_default(password, self.config.password,
                           err_msg='password required')
    if username and not username == self.config.username:
        self.config.username = username
    if password and not password == self.config.password:
        self.config.password = password

    self._load_session()  # new session
    result = self._post('login', username=username,
                        password=password, api_url=False)
    if result:
        self.config['username'] = username
        self.config['password'] = password
    self.cookiejar_save()
    self.logged_in = True
    return result


def logout(self):
    '''
    Log a user out by nulling their secrete cookie key
    '''
    result = self._post('logout', api_url=False)
    self._load_session()  # new session
    # FIXME: logged_in should be set during _load_session()
    self.logged_in = False
    return result


def update_passwd(self, new_password, old_password=None,
                  username=None, save=False):
    '''
    Update existing user's password

    :param String new_password: New user password to set
    :param String old_password: Old user password to unset
    :param String username: Name of the user to manipulate
    :param bool save: update local config file with new password
    '''
    username = set_default(username, self.config.username)
    if not new_password:
        raise ValueError("new password required")
    cmd = os.path.join(username, 'passwd')
    response = self._post(cmd,
                          username=username,
                          old_password=old_password,
                          new_password=new_password,
                          api_url=False,
                          allow_redirects=False,
                          full_response=True)

    if response.status_code == 302 and username == self.config.username:
        self._load_session()
        self.config.password = new_password
        if save:
            self.config.save()

    if response.headers.get('location') == '/login':
        login(self, self.config.username, self.config.password)

    return True


# FIXME: prefix api_url with _ to indicate it's a special kwarg
def update_profile(self, username=None, gnupg=None):
    '''
    Update existing user profile properties

    :param String username: Name of the user to manipulate
    :param String gnupg: update gnupg profile settings
    '''
    username = username or self.config.username
    cmd = os.path.join(username, 'update_profile')
    result = self._post(cmd, gnupg=gnupg, api_url=False)
    return result


def update_properties(self, username=None, backup=True, cube_quota=None):
    '''
    Update existing system level user properties

    :param String username: Name of the user to manipulate
    :param String backup: request previous state of property values
    :param int cube_quota: cube quota count to set
    '''
    username = set_default(username, self.config.username)
    cmd = os.path.join(username, 'update_properties')
    result = self._post(cmd, backup=backup, cube_quota=cube_quota,
                        api_url=False)
    return result
