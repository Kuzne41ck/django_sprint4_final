from django.contrib import admin

from .models import Category, Comment, Location, Post


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Основные поля", {"fields": ("name", "is_published")}),
        (
            "Дополнительно",
            {"fields": ("created_at",), "classes": ("collapse",)},
        ),
    ]
    list_display = ("name", "is_published", "created_at")
    list_filter = ("is_published", "created_at")
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            "Основная информация",
            {"fields": ("title", "description", "slug", "is_published")},
        ),
        (
            "Дополнительно",
            {"fields": ("created_at",), "classes": ("collapse",)},
        ),
    ]
    list_display = ("title", "is_published", "created_at")
    list_filter = ("is_published", "created_at")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            "Основная информация",
            {
                "fields": (
                    "title",
                    "text",
                    "author",
                    "pub_date",
                    "is_published",
                    "category",
                    "location",
                    "image",
                )
            },
        ),
        (
            "Дополнительно",
            {"fields": ("created_at",), "classes": ("collapse",)},
        ),
    ]
    list_display = (
        "title",
        "author",
        "is_published",
        "pub_date",
        "category",
        "location",
        "created_at",
    )
    list_filter = ("is_published", "pub_date", "category", "location")
    search_fields = ("title", "text")
    list_editable = ("is_published",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "post", "created_at")
    list_filter = ("created_at",)
    search_fields = ("text",)
