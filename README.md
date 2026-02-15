# 🔒 OCR + AI Summarizer Pro

A production-ready web application with advanced features: OCR, AI summarization, analytics, history tracking, batch processing, and PDF support.

## 🚀 Features

### Core Features
- **User Authentication**: Secure signup/login with bcrypt password hashing
- **Camera Capture**: Take photos directly or upload images
- **OCR Processing**: Extract text from images using OCR.space API
- **PDF Support**: Extract text from PDF files
- **Multi-language OCR**: Support for 25+ languages
- **AI Summarization**: Generate summaries using OpenAI GPT-3.5
- **Multi-language Summary**: Get summaries in 12+ languages
- **💻 Script Analyzer**: Extract code from images and analyze with AI (bug detection, code review, explanations)

### Advanced Features
- **📊 Analytics Dashboard**: View statistics, token usage, processing time
- **📚 History Tracking**: Save and view all your OCR results
- **🔍 Search Functionality**: Search through your processing history
- **⚡ Batch Processing**: Process multiple images/PDFs at once
- **📧 Email Notifications**: Get notified when processing is complete (optional)
- **📥 Download Results**: Export summaries as text files
- **🗑️ Delete History**: Manage your saved results

### Statistics Tracked
- Total files processed
- Total tokens used
- Average processing time
- Active days
- Language usage patterns

## 📋 Tech Stack

- **Frontend**: Streamlit
- **OCR**: OCR.space API (Cloud-based, no installation required)
- **LLM**: OpenAI GPT-3.5-turbo
- **Database**: Neon PostgreSQL
- **Authentication**: bcrypt
- **Language**: Python 3.8+

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Neon PostgreSQL account
- OpenAI API key
- Internet connection (for cloud OCR)

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd ocr-llm-project
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

1. Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```

2. Edit `.env` and add your credentials:
```
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
```

### Step 5: Set Up Neon Database

1. Go to [Neon Console](https://console.neon.tech/)
2. Create a new project
3. Copy the connection string
4. The application will automatically create the `users` table on first run

**Manual Table Creation (Optional)**:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Step 6: Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
ocr-llm-project/
│
├── app.py                    # Main Streamlit application
├── auth.py                   # Authentication logic
├── database.py               # Database connection and operations
├── ocr.py                    # OCR text extraction
├── llm_agent.py              # OpenAI LLM agent
├── script_analyzer.py        # Code analysis module
├── pdf_ocr.py                # PDF text extraction
├── email_notifications.py    # Email notification system
├── google_oauth.py           # Google Sign-In integration
├── google_auth.py            # Google authentication helper
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not in git)
├── .env.example              # Example environment file
└── README.md                 # Documentation
```

## 🔐 Security Features

- Password hashing with bcrypt
- Parameterized SQL queries (SQL injection prevention)
- Environment variables for sensitive data
- Session-based authentication
- Secure database connection with SSL

## 📝 Usage

### Dashboard
1. **Sign Up/Login**: Create account or login
2. **Choose Input**:
   - Upload Image (JPG, PNG, JPEG)
   - Take Photo with camera
   - Upload PDF file
3. **Configure**:
   - Summary Length: Short/Medium/Detailed
   - Summary Language: English, Arabic, Urdu, etc.
   - OCR Language: Auto-detect or specific
   - Email notification (optional)
4. **Process**: Click "Extract & Summarize"
5. **View & Download**: See results and download

### Analytics
- View total processed files
- Check token usage
- See average processing time
- Track active days

### History
- View all past results
- Search by filename or content
- Delete old entries
- Re-download summaries

### Batch Processing
- Upload multiple files at once
- Process all simultaneously
- Download combined results
- Automatic history saving

### Script Analyzer
- Upload images of code/scripts
- Automatic programming language detection
- Four analysis types:
  - **Full Analysis**: Complete code review with best practices
  - **Bug Detection**: Identify syntax, logic, and runtime errors
  - **Code Review**: Quality, readability, and maintainability assessment
  - **Explanation**: Step-by-step code explanation
- Multi-language output (English, Urdu)
- Download extracted code and analysis
- Syntax highlighting for code display

## 🌍 Supported Languages

### OCR (Text Extraction)
- Auto Detect
- English
- Arabic
- Urdu
- And 20+ more languages

### Summary Output
- English
- Arabic
- Urdu
- Spanish
- French
- German
- Chinese
- Japanese
- Korean
- Russian
- Hindi
- Portuguese

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Required
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=your_neon_database_url

# Optional - Google Sign-In
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com

# Optional - Email Notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

### Google Sign-In Setup (Optional)

To enable "Continue with Google":

1. **Create Google OAuth Credentials:**
   - Go to: https://console.cloud.google.com/apis/credentials
   - Create a new project or select existing
   - Click "Create Credentials" → "OAuth 2.0 Client ID"
   - Application type: "Web application"
   - Authorized redirect URIs: `http://localhost:8501`
   - Copy the Client ID

2. **Update .env:**
   ```bash
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   ```

3. **Restart App:**
   ```bash
   streamlit run app.py
   ```

Now users can sign in with Google! Data is securely stored in Neon PostgreSQL.

### Email Setup (Optional)

To enable email notifications:

1. **Gmail Setup:**
   - Go to Google Account settings
   - Enable 2-Factor Authentication
   - Generate App Password: https://myaccount.google.com/apppasswords
   - Copy the 16-character password

2. **Update .env:**
   ```bash
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-16-char-app-password
   ```

3. **Restart App:**
   ```bash
   streamlit run app.py
   ```

Now email notifications will work when you check "Email me" option!

## 🔧 Configuration

### Summary Lengths

- **Short**: 2-3 sentence summary
- **Medium**: 1-2 paragraph summary
- **Detailed**: Comprehensive summary with sections

### OpenAI Settings

- Model: `gpt-3.5-turbo`
- Temperature: `0.6`
- Max Tokens: `500`

## 🐛 Troubleshooting

### OCR Not Working
- Ensure you have internet connection (cloud-based OCR)
- Check image quality and text clarity
- Supported formats: JPG, PNG, JPEG

### Database Connection Issues
- Verify DATABASE_URL in .env file
- Check Neon project is active
- Ensure SSL mode is enabled

### OpenAI API Errors
- Verify API key is valid
- Check API quota and billing
- Ensure internet connection

## ✅ Tested & Verified

All components have been tested and verified:
- ✅ Database connection
- ✅ User authentication
- ✅ OCR text extraction
- ✅ LLM summarization
- ✅ Complete workflow

Run `python test_complete.py` to verify your setup.

## 📦 Dependencies

- `streamlit`: Web UI framework
- `easyocr`: OCR engine
- `openai`: OpenAI API client
- `psycopg2-binary`: PostgreSQL adapter
- `bcrypt`: Password hashing
- `python-dotenv`: Environment variable management
- `Pillow`: Image processing
- `numpy`: Array operations

## 🚀 Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Add secrets in Streamlit dashboard
4. Deploy

### Environment Variables for Deployment

Add these in your deployment platform:
```
OPENAI_API_KEY=your_key
DATABASE_URL=your_neon_url
```

## 📄 License

MIT License

## 👨‍💻 Author

Built with ❤️ for hackathons and production use

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📞 Support

For issues or questions, please open a GitHub issue.
