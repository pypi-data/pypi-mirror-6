# copyright 2010-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""plugin authentication retriever

:organization: Logilab
:copyright: 2010-2011 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""

__docformat__ = "restructuredtext en"

import hmac

from cubicweb import AuthenticationError
from cubicweb.server.sources import native


class UserSecretKeyAuthentifier(native.BaseAuthentifier):
    """ Provide an authentication procedure based on a private key ``token`` """

    def authenticate(self, session, login, **kwargs):
        """Authentication procedure.

        :login: identifier for the token (see ``AuthToken`` entity)

        Expected kwargs are:

        :signature: signature of the request.
        :request: canonicalized version of the request, used to compute the signature
        """
        session.debug('authentication by %s', self.__class__.__name__)
        signature = kwargs.get('signature')
        request = kwargs.get('request')
        if signature is None or request is None:
            raise AuthenticationError('authentication failure')
        try:
            rset = session.execute('Any U, K WHERE T token_for_user U, '
                                   '               T token K, '
                                   '               T enabled True, '
                                   '               T id %(id)s',
                                   {'id': login})
            if not rset:
                raise AuthenticationError('invalid credentials')
            assert len(rset) == 1
            user_eid, secret_key = rset[0]
            expected_signature = hmac.new(str(secret_key), request).hexdigest()
            if expected_signature == signature:
                return user_eid
            else:
                self.info('request content signature check failed')
        except Exception, exc:
            session.debug('authentication failure (%s)', exc)
        raise AuthenticationError('invalid credentials')
