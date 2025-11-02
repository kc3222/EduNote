import { useEffect, useState } from "react";
import { signup, me, logout } from "./api";

export default function Signup({ onLogin, onSwitchToLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const userData = await me();
        setUser(userData);
        // If user is already logged in, call onLogin
        if (userData && onLogin) {
          onLogin(userData);
        }
      } catch (error) {
        // If me() fails, user is not logged in
        setUser(null);
      } finally {
        setLoading(false);
      }
    })();
  }, [onLogin]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErr("");
    try {
      const u = await signup(email, password);
      setUser(u);
      // Call onLogin callback to notify parent component
      if (onLogin) {
        onLogin(u);
      }
    } catch (e) {
      setErr(e.message);
    }
  };

  const handleLogout = async () => {
    await logout();
    setUser(null);
  };

  // Add loading state check
  if (loading) {
    return (
      <div style={styles.fullscreen}>
        <div style={styles.card}>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (user?.email) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <h2>Welcome</h2>
          <p>You're signed in as <b>{user.email}</b></p>
          <button style={styles.button} onClick={handleLogout}>Log out</button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.fullscreen}>
      <form style={styles.card} onSubmit={handleSubmit}>
        <h2>Sign up</h2>
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
          autoComplete="new-password"
          required
        />
        {err && <div style={styles.error}>{err}</div>}
        <button style={styles.button} type="submit">Sign up</button>
        <button style={styles.loginButton} type="button" onClick={() => onSwitchToLogin?.()}>Back</button>
      </form>
    </div>
  );
}

const styles = {
  fullscreen: {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
    background: "linear-gradient(135deg, #FDE2E4 0%, #E2F0CB 45%, #CDE7F0 100%)"
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
  loginButton: {
    marginTop: 10,
    width: "100%",
    padding: "12px 14px",
    borderRadius: 12,
    border: "1px solid #e5e7eb",
    background: "transparent",
    color: "#475569",
    fontWeight: 600,
    cursor: "pointer",
    boxShadow: "none"
  },
  error: {
    marginTop: 10,
    padding: "10px 12px",
    borderRadius: 10,
    background: "#FDE2E4",
    border: "1px solid #FECACA",
    color: "#7f1d1d"
  },
  container: {
    position: "fixed",
    inset: 0,
    display: "grid",
    placeItems: "center",
    padding: 24,
    background: "linear-gradient(135deg, #FDE2E4 0%, #E2F0CB 45%, #CDE7F0 100%)"
  }
};

