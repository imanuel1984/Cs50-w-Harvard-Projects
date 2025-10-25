document.addEventListener('DOMContentLoaded', () => {

  // Like buttons
  document.querySelectorAll('.like-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const postId = btn.dataset.postId;
      fetch(`/post/${postId}/like/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
      })
      .then(r => r.json())
      .then(data => {
        document.getElementById(`likes-count-${postId}`).innerText = data.likes_count;
        btn.innerText = data.liked ? 'Unlike' : 'Like';
      });
    });
  });

  // Edit posts inline
  document.querySelectorAll('.edit-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const postId = btn.dataset.postId;
      const p = document.getElementById(`post-text-${postId}`);
      const original = p.innerText.trim();

      const textarea = document.createElement('textarea');
      textarea.value = original;
      textarea.rows = 4;
      textarea.style.width = '100%';

      const save = document.createElement('button');
      save.innerText = 'Save';
      const cancel = document.createElement('button');
      cancel.innerText = 'Cancel';

      p.replaceWith(textarea);
      btn.style.display = 'none';
      btn.parentNode.appendChild(save);
      btn.parentNode.appendChild(cancel);

      cancel.addEventListener('click', () => {
        textarea.replaceWith(p);
        save.remove();
        cancel.remove();
        btn.style.display = '';
      });

      save.addEventListener('click', () => {
        const content = textarea.value.trim();
        fetch(`/post/${postId}/edit/`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
          },
          body: JSON.stringify({ content: content })
        })
        .then(resp => {
          if (!resp.ok) return resp.json().then(err => Promise.reject(err));
          return resp.json();
        })
        .then(data => {
          const newP = document.createElement('p');
          newP.id = `post-text-${postId}`;
          newP.className = 'post-text';
          newP.innerHTML = content.replace(/\n/g, '<br>');
          textarea.replaceWith(newP);
          save.remove();
          cancel.remove();
          btn.style.display = '';
        })
        .catch(err => {
          alert(err.error || 'Error updating post.');
        });
      });
    });
  });

  // Follow/unfollow on profile
  const followBtn = document.getElementById('follow-btn');
  if (followBtn) {
    followBtn.addEventListener('click', () => {
      const username = followBtn.dataset.username;
      fetch(`/user/${username}/follow/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
      })
      .then(r => r.json())
      .then(data => {
        followBtn.innerText = data.status === 'followed' ? 'Unfollow' : 'Follow';
        // Optionally update followers count on page if you render it with an id
      });
    });
  }

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let c of cookies) {
        c = c.trim();
        if (c.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(c.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
 