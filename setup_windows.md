# FastTTS Windows Setup Guide

## Prerequisites

1. **Python 3.8 or higher** - Download from [python.org](https://www.python.org/downloads/)
   - During installation, make sure to check "Add Python to PATH"

2. **Git** - Download from [git-scm.com](https://git-scm.com/downloads)

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/CGAlei/FastTTS.git
cd FastTTS
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create Environment File
Create a `.env` file in the root directory with your API keys:
```env
OPENAI_API_KEY=your_openai_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
```

### 5. Initialize Database
The application will automatically create the SQLite database on first run.

### 6. Run the Application
```bash
python main.py
```

The application will start on `http://localhost:5001`

## Features

- **Text-to-Speech**: Supports Edge TTS and Minimax TTS engines
- **Chinese Text Support**: Automatic Traditional/Simplified conversion
- **Vocabulary Management**: Track and rate word difficulty
- **Session Management**: Save and replay TTS sessions
- **Audio Alignment**: Word-level timing synchronization

## Usage

1. Open your browser to `http://localhost:5001`
2. Enter text in the input box
3. Select TTS engine (Edge TTS or Minimax)
4. Choose voice and adjust settings
5. Click "Generate Audio" to create speech
6. Use the karaoke-style player to follow along

## Troubleshooting

### Common Issues

1. **Port 5001 already in use**
   - Change the port in `main.py` (look for `port=5001`)

2. **Missing dependencies**
   - Make sure virtual environment is activated
   - Run `pip install -r requirements.txt` again

3. **Database errors**
   - Delete the `db/` folder and restart the app

4. **TTS not working**
   - Check your internet connection
   - Verify API keys in `.env` file

## Optional: MFA Alignment

For advanced word-level alignment, you can install Montreal Forced Alignment (MFA):

1. Install MFA following their [Windows installation guide](https://montreal-forced-alignment.readthedocs.io/en/latest/installation.html)
2. The application will automatically detect and use MFA if available

## Project Structure

```
FastTTS/
├── main.py              # Main application entry point
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
├── alignment/           # MFA alignment modules
├── components/          # UI components
├── config/              # Configuration files
├── routes/              # API routes
├── static/              # CSS/JS files
├── tts/                 # TTS engines
├── utils/               # Utility functions
└── db/                  # SQLite database (auto-created)
```

## Support

If you encounter issues, check the console output for error messages. Most problems are related to missing dependencies or API key configuration.