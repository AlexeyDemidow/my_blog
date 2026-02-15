from django.contrib import admin

from .models import Post, PostImage, PostLike, Comment, CommentLike


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
    fields = ('image',)
    readonly_fields = ('uploaded_at',)


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    fields = ('user', 'text', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'short_content', 'created_at', 'likes_count', 'comments_count')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'author__username')

    inlines = [PostImageInline, CommentInline]

    def short_content(self, obj):
        content = obj.content or ""
        return content[:40] + "..." if len(content) > 40 else content

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = "Likes"

    def comments_count(self, obj):
        return obj.comments.count()
    comments_count.short_description = "Comments"


@admin.register(PostLike)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'post__content')


@admin.register(CommentLike)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'comment', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'comment__text')


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'image', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('post__content',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'text', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('text', 'user__username', 'post__content')
