from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # API
    path('api/', include('api.urls')),

    # Pages
    path('', TemplateView.as_view(template_name="index.html"), name='index'),
    path('home/', TemplateView.as_view(template_name="home.html"), name='home'),
    path('products/', TemplateView.as_view(template_name="products.html"), name='products'),
    path('cart/', TemplateView.as_view(template_name="cart.html"), name='cart'),
    path('recommendations/', TemplateView.as_view(template_name="recommendations.html"), name='recommendations'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
