# FastTTS - Advanced Text-to-Speech Application

A powerful Text-to-Speech application with word-level synchronization, vocabulary management, and multiple TTS engine support.

## Features

- **Multiple TTS Engines**: Support for Edge TTS and Minimax TTS
- **Word-Level Synchronization**: Precise timing using Montreal Forced Alignment (MFA)
- **Vocabulary Management**: Track and rate word difficulty
- **Session Management**: Save and replay TTS sessions
- **Web Interface**: Modern, responsive UI with karaoke-style playback
- **AI Integration**: LLM support for enhanced functionality

## Installation

### Prerequisites

- Python 3.10+
- Conda/Miniconda
- Git

### Setup

1. **Clone the repository**:
```bash
git clone https://github.com/YOUR_USERNAME/FastTTS.git
cd FastTTS
```

2. **Create conda environment**:
```bash
conda env create -f environment.yml
conda activate fasttts-mfa
```

3. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Usage

### Basic Usage

```bash
# Start the application
python main.py

# Or use the launcher scripts
./launch-fasttts.sh       # Linux/Mac
launch-fasttts.bat        # Windows
```

### With MFA Support

```bash
# Start with Montreal Forced Alignment
./start_fasttts_mfa.sh    # Linux/Mac
start_fasttts_mfa.bat     # Windows
```

## Configuration

- **API Keys**: Configure in `.env` file
- **TTS Engines**: Modify `config/defaults.py`
- **Database**: SQLite database in `db/` directory

## Testing

```bash
# Run tests
python -m pytest test_AI/

# Run rating tests
python run_rating_tests.py
```

## Project Structure

```
FastTTS/
├── main.py                 # Application entry point
├── components/             # UI components
├── tts/                   # TTS engine implementations
├── alignment/             # MFA alignment tools
├── routes/                # Web routes
├── static/                # CSS/JS assets
├── utils/                 # Utility functions
├── config/                # Configuration files
└── test_AI/               # Test suite
```

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions, please open an issue on GitHub.