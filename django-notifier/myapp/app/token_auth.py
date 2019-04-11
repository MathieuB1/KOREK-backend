import jwt, re
import traceback
from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser
from django.conf import LazySettings
from jwt import InvalidSignatureError, ExpiredSignatureError, DecodeError
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

settings = LazySettings()

from django.db import close_old_connections

class TokenAuthMiddleware:
    """
    Token authorization middleware for Django Channels 2
    """
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        # Close old database connections to prevent usage of timed out connections
        close_old_connections()

        # Login with JWT
        try:
            if scope['subprotocols'][0] != 'None':
                
                token = scope['subprotocols'][0]

                try:
                    user_jwt = jwt.decode(
                        token,
                        settings.SECRET_KEY,
                    )
                    scope['user'] = User.objects.get(id=user_jwt['user_id'])
                    return self.inner(scope)

                except (InvalidSignatureError, KeyError, ExpiredSignatureError, DecodeError):
                    traceback.print_exc()
                    pass
                except Exception as e:  # NoQA
                    print(scope)
                    traceback.print_exc()
            else:
                raise

        # Try Session login
        except:
            try:
                session_key = ''
                for name, value in scope['headers']:
                    if name == b'cookie':
                        session_key = value.decode('utf-8').split('sessionid=')[1]

                        session = Session.objects.get(session_key=session_key)
                        session_data = session.get_decoded()
                        uid = session_data.get('_auth_user_id')
                        scope['user'] = User.objects.get(id=uid)
                        break

            # No credentials found so Set Anonymous user
            except:
                scope['user'] = AnonymousUser()

            return self.inner(scope)


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))