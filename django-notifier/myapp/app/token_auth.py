import jwt, re
import traceback
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.conf import LazySettings
from jwt import InvalidSignatureError, ExpiredSignatureError, DecodeError
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

settings = LazySettings()

from django.db import close_old_connections

@database_sync_to_async
def close_connections():
    close_old_connections()

@database_sync_to_async
def get_user(user_jwt):
    try:
        return User.objects.get(id=user_jwt)
    except User.DoesNotExist:
        return AnonymousUser()

@database_sync_to_async
def get_session(session_key):
    try:
        return Session.objects.get(session_key=session_key)
    except Session.DoesNotExist:
        return AnonymousUser()

class TokenAuthMiddleware:
    """
    Token authorization middleware for Django Channels 2
    see:
    https://channels.readthedocs.io/en/latest/topics/authentication.html#custom-authentication
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        return TokenAuthMiddlewareInstance(scope, self)

class TokenAuthMiddlewareInstance:
    """
    Token authorization middleware for Django Channels 2
    """
    def __init__(self, scope, middleware):
        self.middleware = middleware
        self.scope = dict(scope)
        self.inner = self.middleware.inner

    async def __call__(self, receive, send):
        # Close old database connections to prevent usage of timed out connections
        close_connections()

        # Login with JWT
        try:
            if self.scope['subprotocols'][0] != 'None':

                token = self.scope['subprotocols'][0]

                try:
                    user_jwt = jwt.decode(
                        token,
                        settings.SECRET_KEY,
                    )
                    self.scope['user'] = await get_user(user_jwt['user_id'])
                    inner = self.inner(self.scope)
                    return await inner(receive, send)

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
                for name, value in self.scope['headers']:
                    if name == b'cookie':
                        session_key = value.decode('utf-8').split('sessionid=')[1]
                        session = await get_session(session_key)
                        session_data = session.get_decoded()
                        uid = session_data.get('_auth_user_id')
                        self.scope['user'] = await get_user(uid)
                        break

            # No credentials found so Set Anonymous user
            except:
                self.scope['user'] = AnonymousUser()
            inner = self.inner(self.scope)
            return await inner(receive, send)


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))