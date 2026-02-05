import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { MainPage } from "./pages/MainPage";
import { RecommendationDetailsPage } from "./pages/RecommendationDetailsPage";

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route
          path="/recommendations/:approachIri"
          element={<RecommendationDetailsPage />}
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
