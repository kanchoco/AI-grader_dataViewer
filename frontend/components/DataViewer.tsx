import { useState, useEffect } from "react";

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
  
  const handleExpertExcel = () => {
  window.open(`${apiUrl}/expert_excel`, "_blank");
  };

  const fetchData = async () => {
    try {
      const res = await fetch(`${apiUrl}/viewer`);
      const data = await res.json();
      setResults(data.results || []);
    } catch (err) {
      console.error(err);
      alert("조회 실패");
    }
  };

  useEffect(() => {
    fetchData();
  }, []);


  return (
    <div className="search-box">

      <button onClick={handleSearch}>
        Search
      </button>

      <button onClick={handleExpertExcel}>
        Expert Excel
      </button>
    </div>

      <table className="viewer-table">
        <thead>
          <tr>
            <th>Rater</th>
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
              <td>{r.rater_id}</td>
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