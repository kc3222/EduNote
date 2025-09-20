import { useEffect, useState } from "react";
import { login, me, logout } from "./api";

export default function Login() {
  const [email, setEmail] = useState("demo@user.com");
  const [password, setPassword] = useState("password123");
  const [user, setUser] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => setUser(await me()))();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErr("");
    try {
      const u = await login(email, password);
      setUser(u);
    } catch (e) {
      setErr(e.message);
    }
  };

  const handleLogout = async () => {
    await logout();
    setUser(null);
  };

  if (user?.email) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <h2>Welcome</h2>
          <p>You’re signed in as <b>{user.email}</b></p>
          <button style={styles.button} onClick={handleLogout}>Log out</button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.fullscreen}>
      <form style={styles.card} onSubmit={handleSubmit}>
        <h2>Sign in</h2>
        <label style={styles.label}>Email</label>
        <input
          style={styles.input}
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="username"
          required
        />
        <label style={styles.label}>Password</label>
        <input
          style={styles.input}
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
          required
        />
        {err && <div style={styles.error}>{err}</div>}
        <button style={styles.button} type="submit">Log in</button>
        <p style={{ marginTop: 8, fontSize: 12, opacity: 0.8 }}>
          Try <code>demo@user.com</code> / <code>password123</code>
        </p>
      </form>
    </div>
  );
}

const styles = {
    fullscreen: {
      position: "fixed",
      inset: 0,                      // fills the viewport regardless of parent
      display: "grid",
      placeItems: "center",          // centers both axes
      padding: 24,
      background:
        "linear-gradient(135deg, #FDE2E4 0%, #E2F0CB 45%, #CDE7F0 100%)" // pastel
    },
    card: {
      width: 380,
      maxWidth: "92vw",
      background: "rgba(255,255,255,0.92)",
      color: "#1f2937",
      borderRadius: 18,
      padding: 24,
      boxShadow: "0 20px 40px rgba(31, 41, 55, 0.15)",
      border: "1px solid rgba(203,213,225,0.6)"
    },
    label: { display: "block", marginTop: 12, marginBottom: 6, fontSize: 14, color: "#475569" },
    input: {
      width: "100%",
      padding: "12px 14px",
      borderRadius: 12,
      border: "1px solid #e5e7eb",
      background: "#fff",
      color: "#0f172a",
      outline: "none",
      boxShadow: "inset 0 1px 2px rgba(0,0,0,0.04)"
    },
    button: {
      marginTop: 14,
      width: "100%",
      padding: "12px 14px",
      borderRadius: 12,
      border: "1px solid rgba(99,102,241,0.25)",
      background: "linear-gradient(90deg, #BDE0FE, #A8DADC)",
      color: "#0b1324",
      fontWeight: 700,
      cursor: "pointer",
      boxShadow: "0 6px 14px rgba(99,102,241,0.20)"
    },
    error: {
      marginTop: 10,
      padding: "10px 12px",
      borderRadius: 10,
      background: "#FDE2E4",
      border: "1px solid #FECACA",
      color: "#7f1d1d"
    }
};
  