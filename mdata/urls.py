from django.contrib import admin
from django.urls import path, include
from vk_create_request.views import home , vk_rusult , download_xlsx
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='Head'),
    path('vk_create_request', vk_rusult, name='Result'),


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
