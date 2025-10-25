from django.contrib import admin
from .models import User, Listing, Bid, Comment, Watchlist


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "is_staff")


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "owner",
        "starting_bid",
        "category",
        "current_price",
        "active",
        "created_at"
    )
    list_filter = ("active", "category", "owner")
    

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "bidder", "amount", "created_at")
    list_filter = ("listing", "bidder", "created_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "author", "created_at","text")
    list_filter = ("listing", "author", "created_at")
    search_fields = ("text",)


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "listing", "added_at")
    list_filter = ("user", "listing")
