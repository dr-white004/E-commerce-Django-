from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("goto/<int:num>", views.goto, name="goto"),
    path("addwatchlist/<int:num>", views.addwatchlist, name="addwatchlist"),
    path("yourwatchlist", views.yourwatchlist, name="yourwatchlist"),
    path("newbid/<int:num>", views.newbid, name="newbid"),
    path("comment/<int:num>", views.comment, name="comment"),
    path("close_auction/<int:num>", views.close_auction, name="close_auction"),
    path("category", views.category, name="category"),
    path("displaycategory/<str:nam>", views.displaycategory, name="displaycategory"),
    path("closedlisting", views.closedlisting, name="closedlisting")


]
