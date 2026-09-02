import { Navigate, Routes, Route } from "react-router-dom";
import { useAuth } from "@clerk/react-router";
import Landing from "./pages/Landing";
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/Profile";

function ProtectedDashboard() {
  const { isLoaded, isSignedIn } = useAuth();

  if (!isLoaded) {
    return null;
  }

  if (!isSignedIn) {
    return <Navigate to="/" replace />;
  }

  return <Dashboard />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/dashboard" element={<ProtectedDashboard />} />
      <Route path="/profile" element={<Profile />} />
    </Routes>
  );
}
