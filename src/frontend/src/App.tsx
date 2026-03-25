import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import DashboardPage from "./pages/DashboardPage";
import StudentsPage from "./pages/StudentsPage";
import SessionsPage from "./pages/SessionsPage";
import AssessmentsPage from "./pages/AssessmentsPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<DashboardPage />} />
        <Route path="students" element={<StudentsPage />} />
        <Route path="sessions" element={<SessionsPage />} />
        <Route path="assessments" element={<AssessmentsPage />} />
      </Route>
    </Routes>
  );
}

export default App;
