from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    # keep default fields (username, email, password).
    pass

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(max_length=1000)
    timestamp = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)

    def is_liked_by(self, user):
        """Return True if this post is liked by the given user."""
        if user.is_authenticated:
            return self.likes.filter(pk=user.pk).exists()
        return False

    class Meta:
        ordering = ['-timestamp']

    def likes_count(self):
        return self.likes.count()

    def __str__(self):
        return f"Post {self.id} by {self.author.username}"

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")  # who follows
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")  # who is followed
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')

    def __str__(self):
        return f"{self.follower} -> {self.followed}"

