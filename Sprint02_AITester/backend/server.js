import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import OpenAI from "openai";

dotenv.config();

const app = express();
app.use(cors({
    origin: ["http://localhost:5173", "http://127.0.0.1:5173"],
    methods: ["GET", "POST"],
    allowedHeaders: ["Content-Type"]
}));
app.use(express.json({ limit: "1mb" }));

const client = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
});

app.post("/api/generate-tests", async (req, res) => {
    try {
        const { code, frameworkContext } = req.body;

        if (!code) {
            return res.status(400).json({ error: "Code is required" });
        }

        const prompt = `
You are an expert React + Node.js test engineer.

Analyze this code and generate meaningful tests.

Code:
${code}

Framework context:
${frameworkContext || "Not provided"}

Return JSON only with:
{
  "behaviorMap": [],
  "risks": [],
  "unitTests": [],
  "integrationTests": [],
  "edgeCases": [],
  "assumptions": [],
  "confidence": "low | medium | high"
}
`;

        const response = await client.chat.completions.create({
            model: "gpt-4.1-mini",
            messages: [{ role: "user", content: prompt }],
            temperature: 0.2,
        });

        const text = response.choices[0].message.content;
        res.json({ result: text });
    } catch (error) {
        console.error("OpenAI error:", error);
        res.status(500).json({
            error: error.message || "Failed to generate tests",
        });
    }
});

app.get("/", (req, res) => {
    res.send("AI Tester backend is running");
});

const PORT = process.env.PORT || 5001;

const server = app.listen(PORT, () => {
    console.log(`Backend running on port ${PORT}`);
});

server.on("error", (err) => {
    console.error("Server error:", err);
});

setInterval(() => { }, 1000);