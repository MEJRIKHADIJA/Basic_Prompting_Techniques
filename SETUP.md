# Setup Instructions

## 1. Install Dependencies
```bash
pip install -r requirements.txt
```

## 2. Set Environment Variables
Before running the application, set your Groq API key:

**Windows (PowerShell):**
```powershell
$env:GROQ_API_KEY = "your-groq-api-key"
$env:GROQ_MODEL = "mixtral-8x7b-32768"  # optional, defaults to mixtral
$env:PORT = "8000"  # optional, defaults to 8000
```

**Windows (Command Prompt):**
```cmd
set GROQ_API_KEY=your-groq-api-key
set GROQ_MODEL=mixtral-8x7b-32768
set PORT=8000
```

**Linux/macOS:**
```bash
export GROQ_API_KEY="your-groq-api-key"
export GROQ_MODEL="mixtral-8x7b-32768"
export PORT="8000"
```

## 3. Run the Application
```bash
python code.py
```

The server will start at `http://127.0.0.1:8000`

## 4. API Endpoints

- **GET** `/` - Serve index.html
- **GET** `/health` - Health check
- **POST** `/api/classify` - Classify with mode (zero-shot or few-shot)
- **POST** `/zero-shot` - Zero-shot classification
- **POST** `/few-shot` - Few-shot classification

### Example Request
```bash
curl -X POST http://127.0.0.1:8000/api/classify \
  -H "Content-Type: application/json" \
  -d '{"review": "This movie was amazing!", "mode": "zero-shot"}'
```

## Available Groq Models
- `mixtral-8x7b-32768` (default)
- `llama2-70b-4096`
- `gemma-7b-it`
And more available on your Groq account

## Get Your Groq API Key
Sign up at https://console.groq.com/ and generate an API key in your account settings.
