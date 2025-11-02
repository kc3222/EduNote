import { useState } from "react";
import Login from "./Login";
import Signup from "./Signup";
import MainPage from "./MainPage";
import { logout } from "./api";

export default function App() {
  const [user, setUser] = useState(null);
  const [showSignup, setShowSignup] = useState(false);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = async () => {
    try {
      await logout(); // Call the logout API
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      setUser(null); // Clear user state regardless of API call success
    }
  };

  if (user) {
    return <MainPage user={user} onLogout={handleLogout} />;
  }

  if (showSignup) {
    return <Signup onLogin={handleLogin} onSwitchToLogin={() => setShowSignup(false)} />;
  }

  return <Login onLogin={handleLogin} onSwitchToSignup={() => setShowSignup(true)} />;
}
