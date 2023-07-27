from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create/<int:user_id>", views.create, name="create"),
    path("listing/<int:auction_id>", views.auction, name="auction"),
    path("listing/user/", views.users_auction, name="user_auctions"),
    path("listing/close/<int:auction_id>",views.close_auction, name="close_auction"),
    path("watchlist/<int:user_id>", views.watchlist, name="watchlist"),
    path("watchlist/update/<int:auction_id>/<str:update>", views.update_watchlist, name='update_watchlist'),
    path("create_comment/<int:auction_id>", views.create_comment, name="create_comment"),
    path("listing/categorize/<int:category_id>", views.categorize, name="categorize")

]
