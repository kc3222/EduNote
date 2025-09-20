export async function login(email, password) {
    const res = await fetch(`/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include", // send/receive cookie
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || "Login failed");
    }
    return res.json();
  }
  
  export async function me() {
    const res = await fetch(`/auth/me`, { credentials: "include" });
    return res.json();
  }
  
  export async function logout() {
    const res = await fetch(`/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
    return res.json();
  }
  