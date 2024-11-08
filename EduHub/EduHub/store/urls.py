# urls.py
from django.contrib import admin
from django.urls import path
from store import views
from .views import product_list, product_detail, buy_product, sell_product, profile_view, register, login_view, confirm_transaction
from django.contrib.auth import views as auth_views  # Import auth views for logout

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('product_list/', views.product_list, name='product_list'),  # Product listing
    path('product/<int:pk>/', views.product_detail, name='product_detail'),  # Product details by ID
    path('buy/<int:pk>/', views.buy_product, name='buy_product'),  # Buy product by ID
    path('sell_product/', views.sell_product, name='sell_product'),  # Sell product form
    path('profile/', views.profile_view, name='profile'),  # User profile page
    path('login/', views.login_view, name='login'),  # Login URL
    path('register/', views.register, name='register'),  # Register URL
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # Logout URL
    path('', views.index, name='home'),  # Homepage (keep it at the end to prevent conflicts)
    path('confirm_transaction/<int:product_id>/', views.confirm_transaction, name='confirm_transaction'),  # Updated mapping
]

# Serving media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
