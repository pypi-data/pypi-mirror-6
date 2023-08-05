#!/usr/bin/env python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# Author: "Chris Ward <cward@redhat.com>

from passlib.hash import sha256_crypt
import re
from tornado.web import authenticated

from metriqued.core_api import MetriqueHdlr

from metriqueu.utils import utcnow

INVALID_USERNAME_RE = re.compile('[^a-z]', re.I)


class AboutMeHdlr(MetriqueHdlr):
    '''
    RequestHandler for seeing your user profile

    action can be addToSet, pull
    role can be read, write, admin
    '''
    @authenticated
    def get(self, owner):
        # FIXME: add admin check
        # if admin, look up anyone is possible
        # otherwise, must be owner or read
        result = self.aboutme(owner=owner)
        self.write(result)

    def aboutme(self, owner):
        self.user_exists(owner)
        mask = ['passhash']
        if self.is_self(owner):
            return self.get_user_profile(owner, mask=mask)
        else:
            mask += []


class LoginHdlr(MetriqueHdlr):
    '''
    RequestHandler for logging a user into metrique
    '''
    def post(self):
        if self.current_user:
            ok, username = True, self.current_user
        else:
            ok, username = self._parse_auth_headers()
            if ok:
                _next = self.get_argument('next', with_json=False)
                if _next:
                    # go ahead and redirect if we expected to be somewhere else
                    self.redirect(_next)
                else:
                    ok = True
            else:
                # FIXME: should we sleep a split sec for failed auth attempts?
                self._raise(401, "this requires admin privleges")
        if ok:
            # bump expiration...
            self.set_secure_cookie("user", username)
        self.logger.debug("AUTH HEADERS ... [%s] %s" % (username, ok))
        self.write(ok)


class LogoutHdlr(MetriqueHdlr):
    '''
    RequestHandler for logging a user out of metrique
    '''
    @authenticated
    def post(self):
        self.clear_cookie("user")
        self.write(True)


# FIXME: if there are no other users configured already
# then the first user registered MUST be added to 'admin' group
class RegisterHdlr(MetriqueHdlr):
    '''
    RequestHandler for registering new users to metrique
    '''
    def post(self):
        # FIXME: add a 'cube registration' lock
        username = self.get_argument('username')
        password = self.get_argument('password')
        result = self.register(username=username,
                               password=password)
        # FIXME: DO THIS FOR ALL HANDLERS! REST REST REST
        # http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
        self.set_status(201, 'Registration successful: %s' % username)
        self.write(result)

    def register(self, username, password=None, null_password_ok=False):
        if INVALID_USERNAME_RE.search(username):
            self._raise(400,
                        "Invalid username; ascii alpha [a-z] characters only!")
        username = username.lower()
        if self.user_exists(username):
            self._raise(409, "user exists")
        passhash = sha256_crypt.encrypt(password) if password else None
        if not (passhash or null_password_ok):
            self._raise(400, "[%s] no password provided" % username)
        cube_quota = self.metrique_config.user_cube_quota
        doc = {'_id': username,
               '_ctime': utcnow(),
               'own': [],
               'read': [],
               'write': [],
               'admin': [],
               '_cube_quota': cube_quota,
               '_passhash': passhash,
               }
        self.user_profile(admin=True).save(doc, upset=True, safe=True)
        self.logger.debug("new user added (%s)" % (username))
        return True


class RemoveHdlr(MetriqueHdlr):
    '''
    RequestHandler for removing existing users to metrique
    '''
    def delete(self, username):
        result = self.remove(username=username)
        self.write(result)

    def remove(self, username):
        username = username.lower()
        if not self.is_admin(username):
            self._raise(403, 'admin privleges required!')
        if not self.user_exists(username):
            self._raise(409, "user does not exist")
        # delete the user's profile
        spec = {'_id': username}
        self.logger.debug(spec)
        self.user_profile(admin=True).remove(spec)

        # remove the user's cubes
        spec = {'owner': username}
        cubes = [x for x in self.cube_profile().find(spec, {'_id': 1})]
        for cube in cubes:
            cube = cube.get('_id')
            self.mongodb_config.db_timeline_admin[cube].drop()

        # FIXME: # remove the user from cube acls?
        self.logger.debug("user removed (%s)" % username)
        return True


class UpdatePasswordHdlr(MetriqueHdlr):
    '''
    RequestHandler for updating existing users password
    '''
    @authenticated
    def post(self, username):
        old_password = self.get_argument('old_password')
        new_password = self.get_argument('new_password')
        result = self.update_passwd(username=username,
                                    old_password=old_password,
                                    new_password=new_password)
        if self.self_in_group('admin'):
            self.write(result)
        else:
            if result:
                self.clear_cookie("user")
            if self.metrique_config.login_url:
                self.redirect(self.metrique_config.login_url)
            else:
                self.write(result)

    def update_passwd(self, username, new_password, old_password=None):
        ''' Change a logged in user's password '''
        # FIXME: take out a lock... for updating any properties
        self.user_exists(username)
        self.requires_owner_admin(username)
        if not new_password:
            self._raise(400, 'new password can not be null')
        if not old_password:
            old_password = ''
        old_passhash = None
        if old_password:
            old_passhash = self.get_user_profile(username, ['_passhash'])
            if old_passhash and sha256_crypt.verify(old_password,
                                                    old_passhash):
                new_passhash = sha256_crypt.encrypt(new_password)
            else:
                self._raise(400, "old password does not match")
        else:
            new_passhash = sha256_crypt.encrypt(new_password)
        self.update_user_profile(username, 'set', '_passhash', new_passhash)
        self.logger.debug("passwd updated (%s)" % username)
        return True


class UpdateGroupHdlr(MetriqueHdlr):
    '''
    RequestHandler for managing user group properties

    action can be addToSet, pull
    role can be admin
    '''
    @authenticated
    def post(self, username):
        action = self.get_argument('action')
        group = self.get_argument('group')
        result = self.update_passwd(username=username,
                                    group=group, action=action)
        self.write(result)

    def update_group(self, username, group, action='addToSet'):
        ''' Change a logged in user's password '''
        self.user_exists(username)
        self.requires_owner_admin(username)
        self.valid_group(group)
        self.valid_action(action)
        self.update_user_profile(username, action, 'groups', group)
        self.logger.debug("group updated (%s)" % username)
        return True


class UpdateProfileHdlr(MetriqueHdlr):
    @authenticated
    def post(self, username=None):
        gnupg = self.get_argument('gnupg')
        result = self.update_profile(username=username,
                                     gnupg=gnupg)
        self.write(result)

    def update_profile(self, username, gnupg=None):
        '''
        update user profile
        '''
        self.user_exists(username)
        self.requires_owner_admin(username)
        reqkeys = ('fingerprint', 'pubkey')
        if not isinstance(gnupg, dict) and sorted(gnupg.keys()) != reqkeys:
            self._raise(400,
                        "gnupg must be a dict with keys pubkey/fingerprint")
        else:
            backup = self.get_user_profile(username)
            self.logger.debug('GPG PubKey Import: %s' % gnupg)
            self.gnupg_pubkey_import(gnupg['pubkey'])
            self.update_user_profile(username, 'set', 'gnupg', gnupg)
        current = self.get_user_profile(username)
        return {'now': current, 'previous': backup}

    def gnupg_pubkey_import(self, gnupg_key):
        return self.metrique_config.gnupg.import_keys(gnupg_key)


class UpdatePropertiesHdlr(MetriqueHdlr):
    '''
    '''
    @authenticated
    def post(self, username=None):
        backup = self.get_argument('backup')
        cube_quota = self.get_argument('_cube_quota')
        result = self.update_properties(username=username,
                                        backup=backup,
                                        cube_quota=cube_quota)
        if result:
            self.write(True)
        else:
            self.write(False)

    def update_properties(self, username, backup=True, cube_quota=None):
        '''
        update global user properties
        '''
        self.user_exists(username)
        self.is_admin(username)
        if backup:
            backup = self.get_user_profile(username)

        spec = {'_id': username}
        cuba_quota = {'_cube_quote': cube_quota}

        # FIXME: make update_user_profile (or new method) to accept
        # a dict to apply not just a single key/value
        update = {'$set': cuba_quota}
        result = self.user_profile(admin=True).update(spec, update,
                                                      safe=True)
        self.logger.debug(
            "user properties updated (%s): %s" % (username, result))
        if backup:
            return backup
        else:
            return True
