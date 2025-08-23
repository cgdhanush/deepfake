import { bindLoginEvents } from './login.js'; // for login page

function renderPage(route) {
  const app = document.getElementById("app");
  app.innerHTML = ""; // Clear previous content
  

  switch (route) {
    case "/":
      app.innerHTML = `
        <nav>
          <a href="#/">Home</a>
          <a href="#/dashboard">Dashboard</a>
          <button id="login-btn">Login</button>
        </nav>
        <h1>Welcome to DeepFake UI</h1>
      `;
      break;

    case "/dashboard":
      app.innerHTML = `
        <nav>
          <a href="#/">Home</a>
          <a href="#/dashboard">Dashboard</a>
        </nav>
        <h2>Dashboard</h2>
        <p>This is a protected page.</p>
      `;
      break;

    default:
      app.innerHTML = "<h2>404 - Page not found</h2>";
  }

  bindEvents();
}

function bindEvents() {
  const loginBtn = document.getElementById("login-btn");
  if (loginBtn) {
    loginBtn.addEventListener("click", () => {
      bindLoginEvents(); // just call it directly
    });
  }
}

function handleRouteChange() {
  const hash = window.location.hash.replace("#", "") || "/";
  renderPage(hash);
}

window.addEventListener("hashchange", handleRouteChange);
window.addEventListener("load", handleRouteChange);
