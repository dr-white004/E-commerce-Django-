from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),  # Landing page for all users
    path("auctions/", views.index, name="index"),  # Active listings
    path("goto/<int:num>", views.goto, name="goto"),
    path("create/", views.create, name="create"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("yourwatchlist/", views.yourwatchlist, name="yourwatchlist"),
    path("addwatchlist/<int:num>", views.addwatchlist, name="addwatchlist"),
    path("closedlisting/", views.closedlisting, name="closedlisting"),
    path("newbid/<int:num>", views.newbid, name="newbid"),
    path("category/", views.category, name="category"),
    path("displaycategory/<str:nam>", views.displaycategory, name="displaycategory"),
    path("search/", views.search_auctions, name="search"),  # Updated to match view name
    path("profile/<str:username>/", views.profile, name="profile"),
    path("close_auction/<int:num>", views.close_auction, name="close_auction"),
    path("comment/<int:num>", views.comment, name="comment"),
]