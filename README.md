# Resume Tailor Agent

An AI-powered resume tailoring tool that automatically selects the most relevant GitHub projects for any job description and generates a tailored LaTeX resume.

[![Resume Tailor Agent Demo](https://img.youtube.com/vi/oLvcVvBSzWM/0.jpg)](https://youtu.be/oLvcVvBSzWM)

🔗 **Live:** https://resume-tailor-agent-cyan.vercel.app

## How It Works

1. Paste a job description into the UI
2. The agent fetches your GitHub repos live via the GitHub API
3. Groq LLM picks the 3 most relevant projects and writes tailored bullet points
4. A LaTeX resume is generated and ready to download
5. Compile in Overleaf to get a PDF

## Tech Stack

**Backend:** FastAPI, LangChain, Groq LLM, GitHub REST API, Python

**Frontend:** React.js (Vite)

## Project Structure

```
resume-tailor-agent/
├── Backend/
│   ├── agent.py        # GitHub fetch, LLM selection, LaTeX generation
│   ├── main.py         # FastAPI server
│   ├── profile.json    # Candidate profile
│   └── .env            # API keys (not committed)
├── Frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── App.css
│   └── package.json
└── README.md
```

## Setup

### Backend

```bash
cd Backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**.env file:**
```
GITHUB_USERNAME=your_github_username
GITHUB_TOKEN=your_github_token
GROQ_API_KEY=your_groq_api_key
```

### Frontend

```bash
cd Frontend
npm install
npm run dev
```

Open `http://localhost:5173`

## Usage

1. Run the backend in `Backend/`
2. Run the frontend in `Frontend/`
3. Paste a job description and click **Generate Resume**
4. Download the `.tex` file and compile in [Overleaf](https://overleaf.com)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tailor` | Generate tailored resume from JD |
| GET | `/download` | Download the generated `.tex` file |

## Screenshots

<img width="1917" height="910" alt="image" src="https://github.com/user-attachments/assets/d4e038c5-6dac-4191-a293-423544373548" />

<img width="1522" height="837" alt="image" src="https://github.com/user-attachments/assets/b6e27730-0454-437f-ad25-4532bf18bc47" />

<img width="1812" height="847" alt="image" src="https://github.com/user-attachments/assets/a061891f-7565-4ff0-8bd8-3cec8174956e" />


