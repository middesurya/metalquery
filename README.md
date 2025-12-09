# MetalQuery - AI-Powered Metallurgy Materials Database

🔩 **MetalQuery** is a production-ready Natural Language to SQL chatbot that allows you to query a metallurgy materials database using plain English.

![MetalQuery Demo](https://img.shields.io/badge/AI-GPT--4-blue) ![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue) ![React](https://img.shields.io/badge/Frontend-React-61DAFB) ![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)

## ✨ Features

- 🤖 **Natural Language Queries** - Ask questions in plain English
- 🔒 **Secure SQL Generation** - Guardrails prevent SQL injection and data modification
- 📊 **Rich Data Display** - Beautiful tables with formatted values and units
- 🔍 **Query Transparency** - View generated SQL with copy functionality
- ⚡ **Real-time Results** - Instant query execution and response
- 🎨 **Production-Ready UI** - Modern, responsive dark-themed interface

## 📊 Database Content

| Category | Count |
|----------|-------|
| Total Materials | 827 |
| Material Categories | 11 |
| Heat Treatments | 34 |
| Standards | ANSI, ISO, DIN |

### Material Properties Available:
- Ultimate Tensile Strength (MPa)
- Yield Strength (MPa)
- Elastic Modulus (MPa)
- Shear Modulus (MPa)
- Density (kg/m³)
- Hardness (Brinell & Vickers)
- Poisson's Ratio
- Elongation (%)

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- OpenAI API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/metalquery.git
   cd metalquery
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Set up the backend**
   ```bash
   cd nlp_service
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

4. **Import metallurgy data**
   ```bash
   python import_metallurgy_data.py --host localhost --port 5432 --dbname postgres --user postgres --password YOUR_PASSWORD
   ```

5. **Start the NLP service**
   ```bash
   python main.py
   ```

6. **Set up the frontend** (in a new terminal)
   ```bash
   cd frontend
   npm install
   npm start
   ```

7. **Open the application**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8001/docs

## 💡 Example Queries

| Question | Description |
|----------|-------------|
| "What steel has the highest tensile strength?" | Find strongest steel |
| "Show aluminum alloys with yield strength above 300 MPa" | Filter by property |
| "Compare properties of SAE 4140 steel" | Get specific material info |
| "Find lightweight materials with high strength" | Multi-criteria search |
| "List all stainless steels" | Category browsing |
| "What are the hardest materials?" | Sort by property |

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React Frontend │────▶│   FastAPI NLP   │────▶│   PostgreSQL    │
│   (Port 3000)    │◀────│  Service (8001) │◀────│   Database      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   OpenAI GPT-4  │
                        │   (SQL Gen)     │
                        └─────────────────┘
```

## 🔒 Security Features

- ✅ **Read-only queries** - Only SELECT statements allowed
- ✅ **SQL injection prevention** - Multi-layer validation
- ✅ **Table restrictions** - Only allowed tables can be queried
- ✅ **Query limits** - Results capped at 100 rows by default
- ✅ **No system table access** - pg_* and information_schema blocked

## 📁 Project Structure

```
metalquery/
├── nlp_service/           # Backend NLP service
│   ├── main.py            # FastAPI application
│   ├── config.py          # Configuration settings
│   ├── guardrails.py      # SQL security validation
│   ├── schema_loader.py   # Database schema introspection
│   ├── prompts.py         # LLM prompts for metallurgy
│   ├── import_metallurgy_data.py  # Data import script
│   └── requirements.txt   # Python dependencies
├── frontend/              # React frontend
│   ├── src/
│   │   ├── App.jsx        # Main application
│   │   └── App.css        # Styles
│   └── package.json       # Node dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

## 🛠️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chat` | POST | Complete chat flow with SQL execution |
| `/api/v1/generate-sql` | POST | Generate SQL from question |
| `/api/v1/format-response` | POST | Format results in natural language |
| `/api/v1/schema` | GET | Get database schema info |
| `/health` | GET | Health check |

## 📄 License

MIT License - feel free to use this project for learning and development.

## 🙏 Acknowledgments

- Material properties data from engineering standards
- OpenAI for GPT-4 language model
- LangChain for LLM orchestration
