# AI Tester for React + Node

AI Tester is a small full-stack app that helps generate test ideas for React, Node, and JavaScript code. Paste code into the frontend, optionally describe the framework context, and the backend asks OpenAI to return structured suggestions for unit tests, integration tests, edge cases, risks, assumptions, and confidence.

## Tech Stack

- Frontend: React, Vite, Axios
- Backend: Node.js, Express, CORS, dotenv
- AI: OpenAI API

## Project Structure

```text
ai-tester-react-node/
├── backend/
│   ├── server.js
│   ├── package.json
│   └── .env
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── App.css
    │   └── index.css
    ├── package.json
    └── vite.config.js
```

## Prerequisites

- Node.js 18 or newer
- npm
- An OpenAI API key

## Environment Variables

Create or update `backend/.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
PORT=5001
```

`PORT` is optional. If it is not provided, the backend uses `5001`.

## Installation

Install backend dependencies:

```bash
cd backend
npm install
```

Install frontend dependencies:

```bash
cd ../frontend
npm install
```

## Running Locally

Start the backend in one terminal:

```bash
cd backend
npm run dev
```

The backend runs at:

```text
http://127.0.0.1:5001
```

Start the frontend in another terminal:

```bash
cd frontend
npm run dev
```

The frontend runs at:

```text
http://localhost:5173
```

## Usage

1. Open the frontend in your browser.
2. Paste a React component, Node route, or JavaScript function.
3. Optionally add testing context, such as `Vitest`, `React Testing Library`, `Supertest`, or `Express`.
4. Click **Generate Tests**.
5. Review the generated JSON test guidance.

## API

### `GET /`

Health check endpoint.

Response:

```text
AI Tester backend is running
```

### `POST /api/generate-tests`

Generates test recommendations for submitted code.

Request body:

```json
{
  "code": "function add(a, b) { return a + b; }",
  "frameworkContext": "Vitest"
}
```

Response body:

```json
{
  "result": "{ ...generated JSON string... }"
}
```

The generated result is expected to include:

- `behaviorMap`
- `risks`
- `unitTests`
- `integrationTests`
- `edgeCases`
- `assumptions`
- `confidence`

## Available Scripts

Backend:

```bash
npm run dev
```

Frontend:

```bash
npm run dev
npm run build
npm run lint
npm run preview
```

## Notes

- The frontend currently posts to `http://127.0.0.1:5001/api/generate-tests`.
- The backend CORS configuration allows `http://localhost:5173` and `http://127.0.0.1:5173`.
- Do not commit real API keys or secrets.
