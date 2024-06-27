from django.contrib import admin
from .models import User, Bid, Auctioning, Comment

# Register your models here.
admin.site.register(User)
admin.site.register(Bid)
admin.site.register(Auctioning)
admin.site.register(Comment)