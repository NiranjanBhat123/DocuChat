from rest_framework_nested import routers
from collections_app.urls import router as collections_router
from .views import ChatSessionViewSet

sessions_router = routers.NestedSimpleRouter(
    collections_router,
    r'collections',
    lookup='collection',
)
sessions_router.register(r'sessions', ChatSessionViewSet, basename='collection-sessions')

urlpatterns = sessions_router.urls