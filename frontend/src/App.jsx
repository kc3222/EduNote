import { useState } from "react";
import Login from "./Login";
import MainPage from "./MainPage";
import { logout } from "./api";

export default function App() {
  const [user, setUser] = useState(null);

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

  return <Login onLogin={handleLogin} />;
}
  