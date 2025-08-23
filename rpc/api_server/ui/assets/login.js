export function bindLoginEvents() {
  openLoginModal();
}

function openLoginModal() {
  // Avoid duplicate modal
  if (document.getElementById("login-modal-overlay")) return;

  // Create overlay
  const overlay = document.createElement("div");
  overlay.id = "login-modal-overlay";
  overlay.style.position = "fixed";
  overlay.style.top = "0";
  overlay.style.left = "0";
  overlay.style.right = "0";
  overlay.style.bottom = "0";
  overlay.style.background = "rgba(0,0,0,0.5)";
  overlay.style.display = "flex";
  overlay.style.justifyContent = "center";
  overlay.style.alignItems = "center";
  overlay.style.zIndex = "9999";

  // Create modal
  const modal = document.createElement("div");
  modal.id = "login-modal";
  modal.style.background = "#fff";
  modal.style.padding = "25px 30px";
  modal.style.borderRadius = "12px";
  modal.style.boxShadow = "0 5px 15px rgba(0,0,0,0.3)";
  modal.style.width = "300px";
  modal.style.fontFamily = "Arial, sans-serif";
  modal.style.color = "#333";

  modal.innerHTML = `
    <h2 style="margin-top:0; text-align:center;">Login</h2>
    <label for="username">Username</label><br />
    <input id="username" type="text" style="width:100%; margin-bottom:15px; padding:8px; font-size:14px;" /><br />
    <label for="password">Password</label><br />
    <input id="password" type="password" style="width:100%; margin-bottom:20px; padding:8px; font-size:14px;" /><br />
    <div style="text-align:right;">
      <button id="login-submit" style="padding: 8px 15px; margin-right: 10px; cursor:pointer;">Submit</button>
      <button id="login-cancel" style="padding: 8px 15px; cursor:pointer;">Cancel</button>
    </div>
  `;

  overlay.appendChild(modal);
  document.body.appendChild(overlay);

  // Cancel button
  document.getElementById("login-cancel").addEventListener("click", closeLoginModal);

  // Submit button
  document.getElementById("login-submit").addEventListener("click", () => {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!username || !password) {
      alert("Please enter username and password.");
      return;
    }

    // TODO: Replace with actual API request
    alert(`Logging in as: ${username}`);

    closeLoginModal();

    // Redirect to dashboard
    window.location.hash = "#/dashboard";
  });
}

function closeLoginModal() {
  const overlay = document.getElementById("login-modal-overlay");
  if (overlay) {
    overlay.remove();
  }
}
