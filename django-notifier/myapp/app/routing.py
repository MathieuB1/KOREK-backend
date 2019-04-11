from channels.routing import ProtocolTypeRouter, URLRouter
import event.routing
from .token_auth import TokenAuthMiddlewareStack


application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': TokenAuthMiddlewareStack(
        URLRouter(
            event.routing.websocket_urlpatterns
        )
    ),
})