# 🤖 Gemini Ethanol Analyzer

AI-powered ethanol blend impact analysis for Indian vehicles using Google Gemini AI.

## 🚀 EC2 Deployment

### Prerequisites
- Python 3.9+
- Google Gemini API key

### Quick Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Start the application
python start.py
```

### Manual Setup
```bash
# Install requirements
pip install -r requirements.txt

# Start backend server
python -m uvicorn backend.main_gemini:app --host 0.0.0.0 --port 8001
```

### Access the App
- **Frontend**: Open `index.html` in browser
- **Backend API**: `http://your-ec2-ip:8001/api/health`

### Configuration
Users need to provide their own Gemini API key in the frontend form.
Get free API key from: https://aistudio.google.com/

## 📁 File Structure
```
├── index.html              # Frontend application
├── backend/
│   └── main_gemini.py      # Gemini AI backend
├── requirements.txt        # Python dependencies
├── start.py               # Startup script
└── DEPLOYMENT.md          # This file
```

## 🔧 Features
- ✅ Single vehicle name input (any brand/model)
- ✅ Real-time Gemini AI analysis
- ✅ Interactive follow-up questions
- ✅ Comprehensive ethanol compatibility reports
- ✅ All Indian vehicle types supported

## 🛡️ Security
- API keys are provided by users
- No sensitive data stored on server
- CORS enabled for cross-origin requests