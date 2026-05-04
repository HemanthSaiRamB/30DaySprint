import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [code, setCode] = useState("");
  const [frameworkContext, setFrameworkContext] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  const generateTests = async () => {
    setLoading(true);
    setResult("");

    try {
      const res = await axios.post("http://127.0.0.1:5001/api/generate-tests", {
        code,
        frameworkContext,
      });

      setResult(res.data.result);
    } catch (error) {
      console.error(error);
      setResult(
        error.response?.data?.error ||
        error.message ||
        "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="container">
      <h1>AI Tester for React + Node</h1>
      <p>Paste code and get unit, integration, and edge-case test suggestions.</p>

      <textarea
        placeholder="Paste React component, Node route, or JS function..."
        value={code}
        onChange={(e) => setCode(e.target.value)}
      />

      <input
        placeholder="Optional: Vitest, RTL, Supertest, Express, etc."
        value={frameworkContext}
        onChange={(e) => setFrameworkContext(e.target.value)}
      />

      <button onClick={generateTests} disabled={loading || !code}>
        {loading ? "Generating..." : "Generate Tests"}
      </button>

      {result && (
        <pre className="result">
          {result}
        </pre>
      )}
    </main>
  );
}

export default App;