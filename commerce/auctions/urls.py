from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<int:listing_id>", views.display_listing, name="display_listing"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:cat_id>", views.categorized_listings, name="categorized_listings"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("remove_from_watchlist", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("add_comment", views.add_comment, name="add_comment"),
    path("close_listing", views.close_listing, name="close_listing"),
    path("place_bid", views.place_bid, name="place_bid"),
]
