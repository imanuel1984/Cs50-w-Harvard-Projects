from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Post, Follow

class NetworkTestCase(TestCase):

    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username="user1", password="pass1")
        self.user2 = User.objects.create_user(username="user2", password="pass2")

        # Create a post by user1
        self.post1 = Post.objects.create(author=self.user1, content="Hello World!")

        # Client instances
        self.client1 = Client()
        self.client2 = Client()
        self.client1.login(username="user1", password="pass1")
        self.client2.login(username="user2", password="pass2")

    # ----------------- Post creation ----------------- #
    def test_create_post(self):
        response = self.client1.post(reverse('create_post'), {"content": "Hello World!"})
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(Post.objects.last().author, self.user1)
        self.assertEqual(Post.objects.last().content, "Hello World!")

    # ----------------- Edit posts ----------------- #
    def test_edit_own_post(self):
        response = self.client1.put(
            reverse('edit_post', kwargs={'post_id': self.post1.id}),
            content_type="application/json",
            data={'content': 'Updated Content'}
        )
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.content, 'Updated Content')
        self.assertEqual(response.status_code, 200)

    def test_edit_other_post_forbidden(self):
        response = self.client2.put(
            reverse('edit_post', kwargs={'post_id': self.post1.id}),
            content_type="application/json",
            data={'content': 'Hacked!'}
        )
        self.post1.refresh_from_db()
        self.assertNotEqual(self.post1.content, 'Hacked!')
        self.assertEqual(response.status_code, 403)

    # ----------------- Like / Unlike ----------------- #
    def test_like_post(self):
        response = self.client2.post(reverse('toggle_like', kwargs={'post_id': self.post1.id}))
        self.post1.refresh_from_db()
        self.assertTrue(self.post1.likes.filter(pk=self.user2.pk).exists())
        self.assertEqual(response.json()['liked'], True)

    def test_unlike_post(self):
        # First like
        self.client2.post(reverse('toggle_like', kwargs={'post_id': self.post1.id}))
        # Then unlike
        response = self.client2.post(reverse('toggle_like', kwargs={'post_id': self.post1.id}))
        self.post1.refresh_from_db()
        self.assertFalse(self.post1.likes.filter(pk=self.user2.pk).exists())
        self.assertEqual(response.json()['liked'], False)

    # ----------------- Following / Unfollowing ----------------- #
    def test_follow_user(self):
        response = self.client1.post(reverse('toggle_follow', kwargs={'username': self.user2.username}))
        self.assertTrue(Follow.objects.filter(follower=self.user1, followed=self.user2).exists())
        self.assertEqual(response.json()['status'], 'followed')

    def test_unfollow_user(self):
        # First follow
        self.client1.post(reverse('toggle_follow', kwargs={'username': self.user2.username}))
        # Then unfollow
        response = self.client1.post(reverse('toggle_follow', kwargs={'username': self.user2.username}))
        self.assertFalse(Follow.objects.filter(follower=self.user1, followed=self.user2).exists())
        self.assertEqual(response.json()['status'], 'unfollowed')

    # ----------------- Profile Page ----------------- #
    def test_profile_view(self):
        response = self.client1.get(reverse('profile', kwargs={'username': self.user1.username}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user1.username)
        self.assertContains(response, self.post1.content)

    # ----------------- Following Posts ----------------- #
    def test_following_posts_view(self):
        # user1 follows user2
        self.client1.post(reverse('toggle_follow', kwargs={'username': self.user2.username}))
        # create a post by user2
        post2 = Post.objects.create(author=self.user2, content="User2 post")
        response = self.client1.get(reverse('following'))
        self.assertContains(response, "User2 post")
        # user2 posts should not appear to user1 if not followed
        self.client1.post(reverse('toggle_follow', kwargs={'username': self.user2.username}))  # unfollow
        response = self.client1.get(reverse('following'))
        self.assertNotContains(response, "User2 post")
