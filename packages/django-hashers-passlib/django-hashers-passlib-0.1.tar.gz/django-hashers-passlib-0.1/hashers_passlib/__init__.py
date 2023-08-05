# -*- coding: utf-8 -*-
#
# This file is part of django-hashers-passlib
# (https://github.com/mathiasertl/django-hashers-passlib).
#
# django-hashers-passlib is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# django-hashers-passlib is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# django-hashers-passlib.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from django.contrib.auth.hashers import BasePasswordHasher


class PasslibHasher(BasePasswordHasher):
    """Base class for all passlib-based hashers."""

    library = "passlib.hash"
    handler = None
    _hasher = None
    _algorithm = None

    def salt(self):
        """Just return None, passlib handles salt-generation."""
        return None

    @property
    def algorithm(self):
        if self._algorithm is None:
            self._algorithm = self.__class__.__name__
        return self._algorithm

    def get_handler(self):
        if self.handler is None:
            return self.algorithm
        return self.handler

    @property
    def hasher(self):
        return getattr(self._load_library(), self.get_handler())

    def verify(self, password, encoded):
        return self.hasher.verify(password, self.to_orig(encoded))

    def encode(self, password, salt=None):
        return self.from_orig(self.hasher.encrypt(password))

    def from_orig(self, hash):
        return '%s$%s' % (self.algorithm, hash)

    def to_orig(self, hash):
        return hash.split('$', 1)[1]


class PasslibCryptSchemeHasher(PasslibHasher):
    def from_orig(self, encrypted):
        return encrypted.lstrip('$')

    def to_orig(self, encoded):
        return '$%s' % encoded


############################
### Archaic Unix Schemes ###
############################
class des_crypt(PasslibHasher):
    pass


class bsdi_crypt(PasslibHasher):
    pass


class bigcrypt(PasslibHasher):
    pass


class crypt16(PasslibHasher):
    pass


#############################
### Standard Unix Schemes ###
#############################
class md5_crypt(PasslibHasher):
    pass


class sha1_crypt(PasslibHasher):
    pass


class sun_md5_crypt(PasslibHasher):
    pass


class sha256_crypt(PasslibHasher):
    pass


class sha512_crypt(PasslibHasher):
    pass


###################################
### Other Modular Crypt Schemes ###
###################################
class apr_md5_crypt(PasslibCryptSchemeHasher):
    handler = 'apr_md5_crypt'
    algorithm = 'apr1'


class bcrypt_sha256(PasslibCryptSchemeHasher):
    handler = 'bcrypt_sha256'
    algorithm = 'bcrypt-sha256'


class phpass(PasslibHasher):
    pass


class pbkdf2_sha1(PasslibCryptSchemeHasher):
    handler = 'pbkdf2_sha1'
    algorithm = 'pbkdf2'


class pbkdf2_sha256(PasslibCryptSchemeHasher):
    handler = 'pbkdf2_sha256'
    algorithm = 'pbkdf2-sha256'


class pbkdf2_sha512(PasslibCryptSchemeHasher):
    handler = 'pbkdf2_sha512'
    algorithm = 'pbkdf2-sha512'


class cta_pbkdf2_sha1(PasslibHasher):
    pass


class dlitz_pbkdf2_sha1(PasslibHasher):
    pass


class scram(PasslibCryptSchemeHasher):
    pass


# bsd_nthash is provided by a converter

#############################
### Standard LDAP schemes ###
#############################
# ldap_md5 is provided by a converter
# ldap_sha1 is provided by a converter
class ldap_salted_md5(PasslibHasher):
    pass


class ldap_salted_sha1(PasslibHasher):
    pass


# ldap_{crypt} provided by a converter
# ldap_plaintext makes no sense to support

#################################
### Non-Standard LDAP Schemes ###
#################################
# ldap_hex_md5 is provided by a converter
# ldap_hex_sha1 is provided by a converter
# ldap_pbkdf2_{digest} is provided by a converter

class atlassian_pbkdf2_sha1(PasslibHasher):
    pass


class fshp(PasslibHasher):
    pass

# roundup_plaintext makes no sense to support

###########################
### SQL Database Hashes ###
###########################
class mssql2000(PasslibHasher):
    pass


class mssql2005(PasslibHasher):
    pass


class mysql323(PasslibHasher):
    pass


class mysql41(PasslibHasher):
    pass

# postgres_md5 is incompatible (requires username for hash)
# oracle10 is incompatible (requires username for hash)

class oracle11(PasslibHasher):
    pass


#########################
### MS Windows Hashes ###
#########################
class lmhash(PasslibHasher):
    pass


class nthash(PasslibHasher):
    pass

# msdcc is incompatible (requires username for hash)
# msdcc2 is incompatible (requires username for hash)


####################
### Other hashes ###
####################
class cisco_pix(PasslibHasher):
    pass


class cisco_type7(PasslibHasher):
    pass

# django_{digest} not supported, for obvious reasons

class grub_pbkdf2_sha512(PasslibHasher):
    pass


class hex_md4(PasslibHasher):
    pass

# hex_md5 is already supported by Django
# hex_sha1 is already supported by Django

class hex_sha256(PasslibHasher):
    pass


class hex_sha512(PasslibHasher):
    pass
