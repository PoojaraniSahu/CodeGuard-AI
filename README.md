# CodeGuard AI 🛡️

**CodeGuard AI** is a professional, AI-powered code analysis platform that automates the code review process. It integrates directly with GitHub to provide real-time feedback on your code quality, security vulnerabilities, and logic bugs using Google's advanced Gemini models.

## 🚀 Live Demo
Check it out on Vercel: [[https://codeguard-ai.vercel.app](https://code-guard-ai-blush.vercel.app/)]

*(Note: Replace the link above with your actual Vercel deployment URL)*

## ✨ Core Features
- **🤖 AI-Driven Reviews**: Uses Gemini 1.5/2.5 Flash for high-speed, accurate code analysis.
- **🔗 Deep GitHub Integration**: Seamlessly connect your repositories via GitHub OAuth.
- **📡 Real-time Webhooks**: Automatically analyzes Pull Requests and Pushes as they happen.
- **🔎 Full Repo Scans**: Perform a comprehensive "Health Check" on your entire codebase with a single click.
- **💬 Automated GitHub Comments**: Automatically posts issues and suggestions directly to your GitHub PRs.
- **📊 Modern Dashboard**: Track connected repositories, review history, and issue severity at a glance.

## 🛠️ Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (Production) / SQLite (Local)
- **AI**: Google Gemini API
- **Deployment**: Vercel
- **Frontend**: Jinja2, Vanilla CSS/JS

## ⚙️ Setup Instructions

### 1. Prerequisites
- Python 3.9+
- A Google AI (Gemini) API Key
- A GitHub OAuth App ([Create one here](https://github.com/settings/developers))

### 2. Local Installation
```bash
# Clone the repository
git clone https://github.com/PoojaraniSahu/CodeGuard-AI.git
cd CodeGuard-AI

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_key
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
WEBHOOK_BASE_URL=http://localhost:8000
DATABASE_URL=sqlite:///./codeguard.db
SECRET_KEY=your_random_secret
```

### 4. Running the App
```bash
uvicorn main:app --reload
```
Open `http://localhost:8000` in your browser.

## 🚢 Deployment (Vercel)
1. Push your code to GitHub.
2. Connect your repository to Vercel.
3. In Vercel Settings, add the environment variables from your `.env` file.
4. **Important**: For production, use a remote **PostgreSQL** database (e.g., Supabase or Vercel Postgres) and set the `DATABASE_URL`.
5. Update `WEBHOOK_BASE_URL` in Vercel to your production domain.

## 📄 License
MIT License. Feel free to use and contribute!
