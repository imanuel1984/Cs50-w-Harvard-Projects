# Network

A social media platform built with Django and JavaScript.  
Allows users to **post, follow, like, and edit posts** — similar to a simplified Twitter clone.

## Features
- User registration, login, and logout with Django authentication.
- Create, edit, and delete posts with instant updates.
- Like and unlike posts with real-time updates.
- Follow and unfollow other users.
- Profile pages displaying user posts and follower stats.
- Pagination for feed navigation.

## Distinctiveness and Complexity
- Combines Django’s backend logic with front-end interactivity using JavaScript (Fetch API).  
- Real-time-like UI without any frontend framework.  
- Multiple database models (User, Post, Follow, Like) with complex relationships.  
- Fully asynchronous actions (likes, edits, follows) without page reloads.  
- Implements pagination and conditional rendering dynamically.  
- Enforces access control — users can only edit their own posts.

## Technologies
- Django  
- Python  
- JavaScript (Fetch API)  
- HTML / CSS  
- SQLite  

## How to Run
python manage.py runserver
## What I Learned

How to design and connect multiple related Django models.

Implementing AJAX with Fetch API for asynchronous updates.

Managing CSRF tokens and secure communication between client and server.

Paginating data and dynamically updating the front end.

Building a responsive and interactive interface with pure Django and JavaScript.

Designing and testing a full CRUD social system with user relationships and permissions.
## View at
 https://youtu.be/-7Xk_SNUO0w?si=QiPz7XH1UpRkfHYu

 ‏⁦⁩
