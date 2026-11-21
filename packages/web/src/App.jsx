
import { useEffect, useState } from "react";

function App() {
  const [problems, setProblems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:5000/api/problems")
      .then((response) => response.json())
      .then((data) => {
        setProblems(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("API Error:", error);
        setLoading(false);
      });
  }, []);

  return (
    <div style={{ padding: "30px" }}>
      <h1>LeetCode Problems</h1>

      {loading ? (
        <p>Loading problems...</p>
      ) : problems.length === 0 ? (
        <p>No problems found or API connection failed.</p>
      ) : (
        problems.map((problem) => (
          <div key={problem.id}>
            <h3>{problem.title}</h3>
            <p>Difficulty: {problem.difficulty}</p>
            <p>Language: {problem.language}</p>
            <hr />
          </div>
        ))
      )}
    </div>
  );
}

export default App;
