// CSRF helper
function getCookie(name) {
  const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return v ? v.pop() : '';
}
const CSRF = getCookie('csrftoken');

document.addEventListener('DOMContentLoaded', () => {
  const requestsContainer = document.getElementById('requests-container');
  const closedContainer = document.getElementById('closed-requests-container');
  const acceptedContainer = document.getElementById('accepted-requests-container');
  const createForm = document.getElementById('create-request-form');
  const showClosedBtn = document.getElementById('show-closed-btn');
  const showAcceptedBtn = document.getElementById('show-accepted-btn');
  const showOpenBtns = document.querySelectorAll('#show-open-btn');
  const role = window.currentUserRole || '';

  // --- Load open requests ---
  async function loadOpenRequests() {
    if (!requestsContainer) return;
    try {
      const res = await fetch('/api/requests/');
      const json = await res.json();

      if (!json.requests) {
        requestsContainer.innerHTML = '<p class="no-requests">Error loading requests.</p>';
        return;
      }

      const reqs = json.requests.filter(r =>
        role === 'volunteer' ? r.status === 'open' : r.status === 'open' || r.status === 'accepted'
      );
      requestsContainer.innerHTML = '';

      if (reqs.length === 0) {
        requestsContainer.innerHTML = '<p class="no-requests">No open requests.</p>';
        return;
      }

      reqs.forEach(r => {
        const card = document.createElement('div');
        card.className = 'request-card ' + (r.status === 'open' ? 'open' : r.status);

        let volHtml = '';
        if (r.volunteer) {
          volHtml = `<div class="volunteer-info">Volunteer: ${r.volunteer.username} — ${r.volunteer.phone || '-'}</div>`;
        } else if (r.no_volunteers_available) {
          volHtml = `<div class="volunteer-info no-volunteers">No volunteers available</div>`;
        }

        card.innerHTML = `
          <div class="request-info">
            <div class="route">${r.pickup} → ${r.destination}</div>
            <div class="status">${r.requested_time} · ${r.status_display}</div>
            <div style="margin-top:6px">Notes: ${r.notes || '-'}</div>
            <div style="margin-top:6px">Sick phone: ${r.phone || '-'}</div>
            ${volHtml}
          </div>
        `;

        // Sick: cancel
        if (role === 'sick' && r.status === 'open' && Number(r.sick_id) === Number(window.currentUserId)) {
          const cancelBtn = document.createElement('button');
          cancelBtn.className = 'button';
          cancelBtn.textContent = 'Cancel';
          cancelBtn.onclick = async () => {
            if (!confirm('Cancel this request?')) return;
            await fetch(`/api/requests/cancel/${r.id}/`, {
              method: 'POST',
              headers: { 'X-CSRFToken': CSRF },
            });
            loadOpenRequests();
          };
          card.appendChild(cancelBtn);
        }

        // Volunteer: accept + reject
        if (role === 'volunteer' && r.status === 'open') {
          const acceptBtn = document.createElement('button');
          acceptBtn.className = 'accept-btn';
          acceptBtn.textContent = 'Accept';
          acceptBtn.onclick = async () => {
            await fetch(`/api/requests/accept/${r.id}/`, {
              method: 'POST',
              headers: { 'X-CSRFToken': CSRF },
            });
            loadOpenRequests();
          };

          const rejectBtn = document.createElement('button');
          rejectBtn.className = 'button';
          rejectBtn.textContent = 'Reject';
          rejectBtn.onclick = async () => {
            const reason = prompt('Optional reason for rejecting:');
            await fetch(`/api/requests/reject/${r.id}/`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF },
              body: JSON.stringify({ reason }),
            });
            loadOpenRequests();
          };

          card.appendChild(acceptBtn);
          card.appendChild(rejectBtn);
        }

        requestsContainer.appendChild(card);
      });
    } catch (err) {
      console.error(err);
      requestsContainer.innerHTML = '<p class="no-requests">Network error.</p>';
    }
  }

  // --- Load closed (for sick) ---
  async function loadClosedRequests() {
    if (!closedContainer) return;
    closedContainer.style.display = 'block';
    if (requestsContainer) requestsContainer.style.display = 'none';
    closedContainer.innerHTML = '<p>Loading closed requests...</p>';

    try {
      const res = await fetch('/api/requests/closed/');
      const json = await res.json();

      if (!json || !Array.isArray(json.requests)) {
        closedContainer.innerHTML = '<p class="no-requests">Error loading closed requests.</p>';
        return;
      }

      const reqs = json.requests;
      closedContainer.innerHTML = '';

      if (reqs.length === 0) {
        closedContainer.innerHTML = '<p class="no-requests">No closed or cancelled requests.</p>';
        return;
      }

      reqs.forEach(r => {
        const div = document.createElement('div');
        div.className = 'request-card closed';

        let extra = '';
        if (r.status === 'cancelled' && r.no_volunteers_available) {
          extra = '<div class="volunteer-info no-volunteers">No volunteers available</div>';
        }

        div.innerHTML = `
          <div class="request-info">
            <div class="route">${r.pickup} → ${r.destination}</div>
            <div class="status">${r.requested_time} · ${r.status_label || r.status_display}</div>
            <div style="margin-top:6px">Notes: ${r.notes || '-'}</div>
            <div style="margin-top:6px">Volunteer: ${
              r.volunteer ? `${r.volunteer.username} (${r.volunteer.phone || '-'})` : '-'
            }</div>
            ${extra}
          </div>
        `;

        // ✅ Delete button for sick
        const delBtn = document.createElement('button');
        delBtn.className = 'button';
        delBtn.textContent = 'Delete';
        delBtn.onclick = async () => {
          if (!confirm('Delete this request?')) return;
          await fetch(`/api/requests/delete/${r.id}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': CSRF },
          });
          loadClosedRequests();
        };
        div.appendChild(delBtn);

        closedContainer.appendChild(div);
      });
    } catch (err) {
      console.error(err);
      closedContainer.innerHTML = '<p class="no-requests">Error loading closed requests.</p>';
    }
  }

  // --- Load accepted (for volunteer) ---
  async function loadAcceptedRequests() {
    if (!acceptedContainer) return;
    acceptedContainer.style.display = 'block';
    acceptedContainer.innerHTML = '<p>Loading accepted requests...</p>';
    try {
      const res = await fetch('/api/requests/accepted/');
      const json = await res.json();
      const reqs = json.requests || [];
      acceptedContainer.innerHTML = '';

      if (reqs.length === 0) {
        acceptedContainer.innerHTML = '<p class="no-requests">No accepted requests.</p>';
        return;
      }

      reqs.forEach(r => {
        const div = document.createElement('div');
        div.className = 'request-card accepted';
        div.innerHTML = `
          <div class="request-info">
            <div class="route">${r.pickup} → ${r.destination}</div>
            <div class="status">${r.requested_time} · ${r.status_display}</div>
            <div style="margin-top:6px">Sick: ${r.sick_username} · ${r.phone || '-'}</div>
            <div style="margin-top:6px">Notes: ${r.notes || '-'}</div>
          </div>
        `;

        // ✅ Done & Delete for volunteers
        const doneBtn = document.createElement('button');
        doneBtn.className = 'button';
        doneBtn.textContent = 'Done & Delete';
        doneBtn.onclick = async () => {
          if (!confirm('Mark done and erase this request?')) return;
          await fetch(`/api/requests/delete/${r.id}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': CSRF },
          });
          loadAcceptedRequests();
        };

        div.appendChild(doneBtn);
        acceptedContainer.appendChild(div);
      });
    } catch (err) {
      console.error(err);
      acceptedContainer.innerHTML = '<p class="no-requests">Error loading accepted requests.</p>';
    }
  }

  // --- Buttons ---
  if (showClosedBtn) {
    showClosedBtn.onclick = async () => {
      await loadClosedRequests();
      showClosedBtn.style.display = 'none';
      showOpenBtns.forEach(b => (b.style.display = 'inline-block'));
      if (requestsContainer) requestsContainer.style.display = 'none';
    };
  }

  if (showAcceptedBtn) {
    showAcceptedBtn.onclick = async () => {
      await loadAcceptedRequests();
      showAcceptedBtn.style.display = 'none';
      showOpenBtns.forEach(b => (b.style.display = 'inline-block'));
      if (requestsContainer) requestsContainer.style.display = 'none';
    };
  }

  showOpenBtns.forEach(b => {
    b.onclick = async () => {
      if (closedContainer) closedContainer.style.display = 'none';
      if (acceptedContainer) acceptedContainer.style.display = 'none';
      showOpenBtns.forEach(s => (s.style.display = 'none'));
      if (showClosedBtn) showClosedBtn.style.display = 'inline-block';
      if (showAcceptedBtn) showAcceptedBtn.style.display = 'inline-block';
      if (requestsContainer) requestsContainer.style.display = 'block';
      await loadOpenRequests();
    };
  });

  // --- Create request ---
  if (createForm) {
    createForm.onsubmit = async e => {
      e.preventDefault();
      const payload = {
        pickup: createForm.querySelector('[name=pickup]').value,
        destination: createForm.querySelector('[name=destination]').value,
        time: createForm.querySelector('[name=time]').value,
        notes: createForm.querySelector('[name=notes]').value,
        phone: createForm.querySelector('[name=phone]').value,
      };

      try {
        const res = await fetch('/api/requests/create/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF },
          body: JSON.stringify(payload),
        });
        const json = await res.json();

        if (json.success) {
          createForm.reset();
          await loadOpenRequests();
        } else {
          alert(json.error || 'Failed to create request');
        }
      } catch (err) {
        console.error(err);
        alert('Network error');
      }
    };
  }

  // --- Initial load ---
  loadOpenRequests();
});
button