const BASE = "http://127.0.0.1:8000";

// REGISTER
async function register() {
  const email = document.getElementById("reg_email").value;
  const password = document.getElementById("reg_password").value;

  const res = await fetch(`${BASE}/register`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ email, password })
  });

  const data = await res.json();
  document.getElementById("reg_msg").innerText = data.message || data.detail;
}

// LOGIN
async function login() {
  const email = document.getElementById("login_email").value;
  const password = document.getElementById("login_password").value;

  const res = await fetch(`${BASE}/login`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ email, password })
  });

  const data = await res.json();

  if (data.access_token) {
    localStorage.setItem("token", data.access_token);
    window.location.href = "dashboard.html";
  } else {
    document.getElementById("login_msg").innerText = data.detail;
  }
}

// PROTECTED
async function getProtectedData() {
  const token = localStorage.getItem("token");

  const res = await fetch(`${BASE}/protected`, {
    headers: {
      "Authorization": `Bearer ${token}`
    }
  });

  const data = await res.json();
  document.getElementById("data").innerText = data.message;
}

// LOGOUT
function logout() {
  localStorage.removeItem("token");
  window.location.href = "login.html";
}