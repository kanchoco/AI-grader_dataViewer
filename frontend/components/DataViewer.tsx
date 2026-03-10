import { useState } from "react";

interface Props {
  apiUrl: string;
}

interface Result {
  student_id: string;
  rater_knw_score: number;
  rater_crt_score: number;
  ai_knw_score: number;
  ai_crt_score: number;
  final_knw_score: number;
  final_crt_score: number;
}

const DataViewer: React.FC<Props> = ({ apiUrl }) => {

  const [raterId, setRaterId] = useState("");
  const [results, setResults] = useState<Result[]>([]);

  const handleSearch = async () => {

    if (!raterId) return;

    try {
      const res = await fetch(`${apiUrl}/viewer/${raterId}`);
      const data = await res.json();

      setResults(data.results || []);
    } catch (err) {
      console.error(err);
      alert("조회 실패");
    }
  };

  return (
    <div className="viewer-container">

      <h2>Rater Result Viewer</h2>

      <div className="search-box">
        <input
          value={raterId}
          onChange={(e) => setRaterId(e.target.value)}
          placeholder="Enter rater ID"
        />

        <button onClick={handleSearch}>
          Search
        </button>
      </div>

      <table className="viewer-table">
        <thead>
          <tr>
            <th>Student</th>
            <th>Rater KNW</th>
            <th>Rater CRT</th>
            <th>AI KNW</th>
            <th>AI CRT</th>
            <th>Final KNW</th>
            <th>Final CRT</th>
          </tr>
        </thead>

        <tbody>
          {results.map((r, i) => (
            <tr key={i}>
              <td>{r.student_id}</td>
              <td>{r.rater_knw_score}</td>
              <td>{r.rater_crt_score}</td>
              <td>{r.ai_knw_score}</td>
              <td>{r.ai_crt_score}</td>
              <td>{r.final_knw_score}</td>
              <td>{r.final_crt_score}</td>
            </tr>
          ))}
        </tbody>
      </table>

    </div>
  );
};

export default DataViewer;