import { useState, useEffect } from "react";
import LoginScreen from "./components/LoginScreen.tsx";
import GradingScreen from "./components/DataViewer.tsx";
import './components/Viewer.css'

// Cloud Run API URL
const API_BASE_URL =
  "test";

function App() {
  return (
    <GradingScreen
      apiUrl={API_BASE_URL}
    />
  );
}

export default App;

