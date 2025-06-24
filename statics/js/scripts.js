console.log("scripts.js loaded");

document.getElementById('register-form').addEventListener('submit', async function (e) {
  e.preventDefault();

  const name = document.getElementById('name').value;
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  const response = await fetch('/api/store/register/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ name, email, password })
  });

  const alertBox = document.getElementById('register-alert');
  const data = await response.json();

  if (response.ok && data.success) {
    alertBox.classList.remove('d-none', 'alert-danger');
    alertBox.classList.add('alert', 'alert-success');
    alertBox.innerText = data.message;
    document.getElementById('register-form').reset();
  } else {
    alertBox.classList.remove('d-none', 'alert-success');
    alertBox.classList.add('alert', 'alert-danger');
    alertBox.innerText = data.errors?.message || 'Something went wrong';
  }
});