import DataViewer from "./components/DataViewer.tsx";
import './components/Viewer.css';

// Cloud Run API URL
const API_BASE_URL =
  "https://ai-assist-grading-1015930710584.us-central1.run.app";

function App() {
  return (
    <DataViewer
      apiUrl={API_BASE_URL}
    />
  );
}

export default App;

