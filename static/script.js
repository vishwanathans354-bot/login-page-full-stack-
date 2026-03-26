let token = localStorage.getItem("token") || "";

// REGISTER
async function register() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/register", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();
    document.getElementById("msg").innerText = JSON.stringify(data);
}

// LOGIN (FORM DATA)
async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);

    const res = await fetch("/login", {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body: form
    });

    const data = await res.json();

    if (data.access_token) {
        token = data.access_token;
        localStorage.setItem("token", token);
        window.location.href = "/dashboard";
    } else {
        document.getElementById("msg").innerText = JSON.stringify(data);
    }
}

// PROTECTED
async function loadData() {
    const res = await fetch("/protected", {
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    const data = await res.json();
    document.getElementById("msg").innerText = JSON.stringify(data);
}