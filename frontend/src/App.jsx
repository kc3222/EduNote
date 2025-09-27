import { useState } from "react";
import Login from "./Login";
import MainPage from "./MainPage";

export default function App() {
  const [user, setUser] = useState(null);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
  };

  if (user) {
    return <MainPage user={user} onLogout={handleLogout} />;
  }

  return <Login onLogin={handleLogin} />;
}
  