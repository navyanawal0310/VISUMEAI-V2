# VisumeAI - AI-Powered Video Resume Evaluator

**An Intelligent Multi-Modal Candidate Assessment Platform**

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Installation & Setup](#installation--setup)
   - [System Requirements](#-system-requirements)
   - [Step 1 — Install System Dependencies](#step-1--install-system-dependencies)
   - [Step 2 — Clone the Repository](#step-2--clone-the-repository)
   - [Step 3 — Backend Setup](#step-3--backend-setup)
   - [Step 4 — Frontend Setup](#step-4--frontend-setup)
   - [Step 5 — Verify Everything Works](#step-5--verify-everything-works)
   - [Troubleshooting](#️-troubleshooting)
3. [System Architecture](#system-architecture)
4. [Pipeline Flow & Algorithm Overview](#pipeline-flow--algorithm-overview)
5. [Detailed Module Algorithms](#detailed-module-algorithms)
6. [Score Aggregation & Final Evaluation](#score-aggregation--final-evaluation)
7. [Key Features](#key-features)
8. [Usage Guide](#usage-guide)
9. [Technology Stack](#technology-stack)
10. [Performance & Limitations](#performance--limitations)

---

## 🎯 Executive Summary

**VisumeAI** is an end-to-end AI-powered platform that evaluates candidate video resumes through multi-modal analysis combining:

- **Visual Analysis**: Body language, eye contact, posture, gestures (MediaPipe)
- **Audio Processing**: Speech-to-text transcription (OpenAI Whisper)
- **NLP Analysis**: Communication quality, vocabulary, coherence (spaCy)
- **Resume Parsing**: Skills, experience, education extraction (PyPDF2, NER)
- **Role Matching**: Semantic similarity with job requirements (SentenceTransformers)
- **Soft Skills Assessment**: Communication, confidence, engagement, professionalism

**Output**: Comprehensive evaluation score (0-100) with detailed feedback, PDF reports, and improvement tracking.

---

## 🚀 Installation & Setup

> **Supports**: Windows 10/11 · macOS 12+ · Ubuntu 20.04+

---

### **📋 System Requirements**

| Requirement | Minimum | Recommended |
|---|---|---|
| **OS** | Windows 10, macOS 12, Ubuntu 20.04 | Latest stable version |
| **Python** | 3.10 | 3.11 |
| **Node.js** | 18.x | 20.x (LTS) |
| **RAM** | 8 GB | 16 GB |
| **Storage** | 5 GB free | 10 GB free |
| **GPU** | — | NVIDIA CUDA (speeds up ML) |

You will also need:
- An **OpenAI API Key** (required – for Whisper audio transcription)
- **FFmpeg** installed on your system (required for audio extraction from video)
- **PostgreSQL 15+** (optional – uses SQLite-compatible fallback if not configured)

---

### **Step 1 — Install System Dependencies**

#### 🪟 Windows

1. **Python 3.10+**
   - Download from [python.org/downloads](https://www.python.org/downloads/)
   - ✅ During install, check **"Add Python to PATH"**
   - Verify: open **Command Prompt (cmd)** and run:
     ```cmd
     python --version
     pip --version
     ```

2. **Node.js 18+ (LTS)**
   - Download from [nodejs.org](https://nodejs.org/)
   - Verify:
     ```cmd
     node --version
     npm --version
     ```

3. **FFmpeg**
   - Download from [ffmpeg.org/download.html](https://ffmpeg.org/download.html) (get the Windows build)
   - Extract the zip, then add the `bin` folder to your system PATH:
     - Search → *Edit environment variables* → *Path* → *New* → paste path to `ffmpeg\bin`
   - Verify:
     ```cmd
     ffmpeg -version
     ```

4. **Git** (to clone the repo)
   - Download from [git-scm.com](https://git-scm.com/download/win)

---

#### 🍎 macOS

Using **Homebrew** ([brew.sh](https://brew.sh)):

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python, Node.js, FFmpeg, Git
brew install python@3.11 node ffmpeg git

# Verify
python3 --version
node --version
ffmpeg -version
```

---

#### 🐧 Ubuntu / Debian Linux

```bash
sudo apt update && sudo apt upgrade -y

# Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Node.js 20 LTS (via NodeSource)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# FFmpeg & Git
sudo apt install -y ffmpeg git

# Verify
python3.11 --version
node --version
ffmpeg -version
```

---

### **Step 2 — Clone the Repository**

```bash
git clone https://github.com/amogh330/VISUMEAI-V2.git
cd VISUMEAI-V2
```

---

### **Step 3 — Backend Setup**

Navigate into the `backend` folder:

```bash
cd backend
```

#### 3a — Create & Activate a Virtual Environment

**Windows (cmd / PowerShell):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> 💡 Your terminal prompt will show `(venv)` when the environment is active.  
> To deactivate later, just run `deactivate`.

---

#### 3b — Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> ⚠️ This installs PyTorch, MediaPipe, spaCy, and other heavy ML libraries.  
> Expect this to take **5–15 minutes** on first run depending on your internet speed.  
> If you have an NVIDIA GPU, see the [PyTorch CUDA install guide](https://pytorch.org/get-started/locally/) for GPU-accelerated builds.

---

#### 3c — Download the spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

---

#### 3d — Configure Environment Variables

Copy the example file and fill in your values:

**Windows:**
```cmd
copy .env.example .env
```

**macOS / Linux:**
```bash
cp .env.example .env
```

Now open `backend/.env` in any text editor and update the values:

```env
# ──────────────────────────────────────────
# API Server
# ──────────────────────────────────────────
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# ──────────────────────────────────────────
# Security  (change this in production!)
# ──────────────────────────────────────────
SECRET_KEY=your-secret-key-change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ──────────────────────────────────────────
# OpenAI  (REQUIRED for transcription)
# ──────────────────────────────────────────
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# ──────────────────────────────────────────
# Llama (OPTIONAL – local AI feedback)
# ──────────────────────────────────────────
LLAMA_API_KEY=your-llama-api-key
LLAMA_API_URL=http://localhost:11434/api/generate

# ──────────────────────────────────────────
# Database  (leave blank to use default SQLite)
# ──────────────────────────────────────────
DATABASE_URL=postgresql://user:password@localhost:5432/visumeai

# ──────────────────────────────────────────
# File Storage
# ──────────────────────────────────────────
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=104857600   # 100 MB

# ──────────────────────────────────────────
# CORS  (add your frontend URL)
# ──────────────────────────────────────────
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# ──────────────────────────────────────────
# spaCy Model
# ──────────────────────────────────────────
SPACY_MODEL=en_core_web_sm
```

> 🔑 **Where to get your OpenAI API Key:** Sign in at [platform.openai.com/api-keys](https://platform.openai.com/api-keys) and create a new secret key.

---

#### 3e — Start the Backend Server

```bash
# Option A – using the startup script
python main.py

# Option B – using Uvicorn directly (supports hot-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

✅ The API will be available at: **http://localhost:8000**  
✅ Interactive API docs (Swagger UI): **http://localhost:8000/docs**

---

### **Step 4 — Frontend Setup**

Open a **new terminal window** (keep the backend running), then:

```bash
cd frontend

# Install all Node.js dependencies
npm install

# Start the Vite development server
npm run dev
```

✅ The app will open at: **http://localhost:5173**

---

### **Step 5 — Verify Everything Works**

1. Open **http://localhost:5173** in your browser.
2. You should see the VisumeAI landing page.
3. Navigate to the **Recruiter Dashboard** and create a test job posting.
4. Navigate to the **Candidate Page**, fill in your name, select the job, and upload a short test video + PDF resume.
5. Click **Evaluate** — the pipeline should run and return a score within ~30–70 seconds.

---

### **🗂️ Project Structure Overview**

```
VISUMEAI-V2/
├── backend/
│   ├── main.py            ← FastAPI entry point
│   ├── requirements.txt   ← Python dependencies
│   ├── .env               ← Your environment config (create this)
│   ├── .env.example       ← Template for .env
│   └── app/               ← Core modules (routes, pipelines, models)
│       └── uploads/       ← Uploaded files stored here
└── frontend/
    ├── package.json       ← Node dependencies
    ├── vite.config.js     ← Vite configuration
    └── src/               ← React source code
```

---

### **🛠️ Troubleshooting**

| Problem | Solution |
|---|---|
| `python` not found on Windows | Use `python3` instead, or re-install Python with PATH enabled |
| `pip install` fails on `mediapipe` | Ensure Python ≤ 3.11; mediapipe doesn't support 3.12+ yet |
| `ffmpeg not found` error | FFmpeg is not in your PATH – see Step 1 |
| `OPENAI_API_KEY` error | Check your `.env` file is in the `backend/` folder |
| Port 8000 already in use | Run `uvicorn main:app --port 8001` and update frontend API URL |
| spaCy model not found | Run `python -m spacy download en_core_web_sm` inside your venv |
| `npm install` fails | Delete `node_modules/` and `package-lock.json`, then retry |
| CORS errors in browser | Add your frontend URL to `CORS_ORIGINS` in `backend/.env` |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Candidate    │  │ Recruiter    │  │ Evaluation   │       │
│  │ Dashboard    │  │ Dashboard    │  │ Page         │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
└─────────┼──────────────────┼──────────────────┼─────────── ─┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼────────┐
                    │   FastAPI       │
                    │   Backend API   │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌──────▼────────┐
│ Video Pipeline │  │ Audio Pipeline  │  │ Resume Parser │
│ (MediaPipe)    │  │ (Whisper API)   │  │ (PyPDF2/NER)  │
└───────┬────────┘  └────────┬────────┘  └──────┬────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  NLP Analyzer   │
                    │    (spaCy)      │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Role Matcher   │
                    │ (Embeddings)    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Soft Skills     │
                    │   Analyzer      │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Score Aggregator│
                    │  (Weighted Sum) │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Feedback & PDF  │
                    │    Generator    │
                    └─────────────────┘
```

---

## 🔄 Pipeline Flow & Algorithm Overview

### **Complete Evaluation Pipeline**

```
INPUT: Video + Resume + Job Description
   │
   ├─► [1] VIDEO PROCESSING
   │   └─► Frame Extraction (every 5th frame)
   │       └─► MediaPipe Analysis (Face, Pose, Hands)
   │           └─► Per-frame Metrics → Temporal Smoothing
   │               └─► Video Scores: eye_contact, posture, gestures, expressiveness
   │
   ├─► [2] AUDIO EXTRACTION
   │   └─► Extract audio track from video
   │       └─► Convert to WAV format
   │           └─► OpenAI Whisper API
   │               └─► Text Transcript
   │
   ├─► [3] RESUME PARSING
   │   └─► Detect format (PDF/DOCX)
   │       └─► Extract text
   │           └─► Keyword Matching + NER
   │               └─► Skills, Experience, Education, Certifications
   │
   ├─► [4] NLP ANALYSIS (on Transcript)
   │   └─► Text Cleaning
   │       └─► spaCy Processing
   │           ├─► Clarity Score (sentence structure, fillers)
   │           ├─► Vocabulary Diversity (TTR)
   │           ├─► Coherence Score (transition words)
   │           └─► Technical Terms Extraction
   │
   ├─► [5] ROLE MATCHING
   │   └─► Gather candidate skills (resume + transcript)
   │       ├─► Skill Overlap (exact matching)
   │       ├─► Experience Check (binary)
   │       └─► Semantic Similarity (embeddings)
   │           └─► Weighted Match Percentage
   │
   ├─► [6] SOFT SKILLS ANALYSIS
   │   └─► Combine Video + Transcript metrics
   │       ├─► Communication (clarity, vocabulary, coherence)
   │       ├─► Confidence (video + sentiment)
   │       ├─► Engagement (expressiveness, gestures, eye contact)
   │       └─► Professionalism (posture, tech terms, coherence)
   │
   └─► [7] SCORE AGGREGATION
       └─► Weighted Combination:
           ├─► Role Match (40%)
           ├─► Soft Skills (30%)
           └─► Video Confidence (30%)
               └─► Overall Score (0-100)
                   └─► Recommendation Level
                       └─► PDF Report Generation
```

---

## 🔬 Detailed Module Algorithms

### **1. Video Processing Pipeline**

**Technology**: MediaPipe (Face Mesh, Pose, Hands)

**Algorithm**:

```python
# Step 1: Frame Sampling
for frame_idx in range(0, total_frames, sample_rate=5):
    frame = extract_frame(video, frame_idx)
    rgb_frame = BGR_to_RGB(frame)
    
    # Step 2: MediaPipe Detection
    face_landmarks = face_mesh.process(rgb_frame)  # 468 points
    pose_landmarks = pose.process(rgb_frame)        # 33 points
    hand_landmarks = hands.process(rgb_frame)       # 21 points/hand
    
    # Step 3: Per-Frame Metrics
    eye_gaze = compute_eye_gaze(face_landmarks)
    head_pose = compute_head_pose(face_landmarks)
    posture = compute_posture(pose_landmarks)
    gestures = compute_gestures(hand_landmarks)
    
    frame_metrics.append({
        'eye_gaze': eye_gaze,
        'posture': posture,
        'gestures': gestures,
        'expressiveness': compute_expressiveness(face_landmarks, gestures)
    })

# Step 4: Temporal Smoothing (Windowed Average)
window_size = 10 frames
for i in range(0, len(frame_metrics), window_size):
    window = frame_metrics[i:i+window_size]
    smoothed_scores.append({
        'eye_contact': mean([f['eye_gaze'] for f in window]),
        'posture': mean([f['posture'] for f in window]),
        'gestures': mean([f['gestures'] for f in window]),
        'expressiveness': mean([f['expressiveness'] for f in window])
    })

# Step 5: Final Aggregation
eye_contact_score = mean([w['eye_contact'] for w in smoothed_scores])
posture_score = mean([w['posture'] for w in smoothed_scores])
gesture_score = mean([w['gestures'] for w in smoothed_scores])
expressiveness_score = mean([w['expressiveness'] for w in smoothed_scores])
```

**Key Formulas**:

**Eye Contact Score** (0-1):
```
eye_x = (left_eye_x + right_eye_x) / 2  # Normalized [0,1]
if 0.35 < eye_x < 0.65:
    score = 1.0  # Centered on camera
else:
    deviation = abs(eye_x - 0.5)
    score = max(0, 1 - deviation * penalty_rate)
```

**Posture Score** (0-1):
```
shoulder_diff = abs(left_shoulder_y - right_shoulder_y)
alignment_score = max(0, 1 - shoulder_diff * multiplier)
```

**Gesture Score** (0-1):
```
hand_visible_frames = count_frames_with_hands()
gesture_score = min(1.0, (hand_visible_frames / total_frames) * 1.5)
```

**Confidence Score** (0-1):
```
confidence = (
    eye_contact * 0.35 +
    posture * 0.35 +
    gestures * 0.15 +
    expressiveness * 0.15
)
```

**Engagement Score** (0-1):
```
engagement = (
    expressiveness * 0.4 +
    gestures * 0.3 +
    eye_contact * 0.3
)
```

**Improvements Applied**:
- **Temporal Smoothing**: Averages metrics over 10-frame windows to reduce noise
- **Relaxed Thresholds**: Eye contact range expanded (0.35-0.65 instead of strict center)
- **Duration Bonuses**: Longer videos (>60s) get small score boosts
- **Confidence Intervals**: Reports 95% confidence ranges for transparency

---

### **2. Audio Processing & Transcription**

**Technology**: pydub + OpenAI Whisper API

**Algorithm**:

```python
# Step 1: Extract Audio
video = VideoFileClip(video_path)
audio = video.audio
audio.write_audiofile("temp_audio.wav", codec='pcm_s16le')

# Step 2: Transcribe
with open("temp_audio.wav", "rb") as audio_file:
    transcript = openai.Audio.transcribe(
        model="whisper-1",
        file=audio_file,
        language="en"
    )

transcript_text = transcript["text"]
```

**Output**: Raw text transcript of spoken content

---

### **3. Resume Parsing Algorithm**

**Technology**: PyPDF2, python-docx, spaCy NER

**Algorithm**:

```python
# Step 1: Format Detection & Text Extraction
if file.endswith('.pdf'):
    text = extract_pdf_text(file)  # PyPDF2
elif file.endswith('.docx'):
    text = extract_docx_text(file)  # python-docx

# Step 2: Skills Extraction
skills = set()

# Method 1: Keyword Matching (100+ predefined terms)
for keyword in TECHNICAL_KEYWORDS:
    if re.search(r'\b' + keyword + r'\b', text, re.IGNORECASE):
        skills.add(keyword.lower())

# Method 2: Named Entity Recognition
doc = nlp(text)
for ent in doc.ents:
    if ent.label_ in ['ORG', 'PRODUCT']:
        if is_technical_term(ent.text):
            skills.add(ent.text.lower())

# Step 3: Experience Extraction
experience_patterns = [
    r'(\d+)\s+years?\s+of\s+experience',
    r'experience:\s*(\d+)\s+years?',
    r'(\d+)\s+years?\s+in'
]
experience_years = max([
    int(match.group(1)) 
    for pattern in experience_patterns 
    for match in re.finditer(pattern, text, re.IGNORECASE)
], default=0)

# Step 4: Education Extraction
education_patterns = {
    'bachelor': r'bachelor|b\.s\.|b\.a\.|b\.tech|b\.e\.',
    'master': r'master|m\.s\.|m\.a\.|m\.tech|m\.b\.a\.',
    'phd': r'phd|ph\.d\.|doctorate'
}
education = [degree for degree, pattern in education_patterns.items() 
             if re.search(pattern, text, re.IGNORECASE)]

# Step 5: Certifications
cert_keywords = ['AWS Certified', 'Azure Certified', 'PMP', 'Scrum Master', ...]
certifications = [cert for cert in cert_keywords 
                  if cert.lower() in text.lower()]
```

**Output**: `ResumeAnalysisResult` with skills, experience_years, education, certifications, tools

---

### **4. NLP Analysis Algorithm**

**Technology**: spaCy (en_core_web_sm)

**Algorithm**:

```python
# Step 1: Text Cleaning
text = re.sub(r'\s+', ' ', transcript)  # Remove extra whitespace
text = text.strip()

# Step 2: spaCy Processing
doc = nlp(text)
sentences = [sent.text for sent in doc.sents]
words = [token.text.lower() for token in doc if token.is_alpha]

# Step 3: Clarity Score (0-1)
avg_sentence_length = len(words) / len(sentences) if sentences else 0
optimal_length = 15
length_score = 1.0 - abs(avg_sentence_length - optimal_length) / optimal_length

punctuation_count = sum(1 for token in doc if token.is_punct)
punctuation_score = min(1.0, punctuation_count / len(sentences))

filler_words = ['um', 'uh', 'like', 'you know', 'so', 'well']
filler_count = sum(1 for word in words if word in filler_words)
filler_penalty = min(1.0, filler_count * 0.05)
filler_score = max(0, 1.0 - filler_penalty)

clarity_score = (
    length_score * 0.4 +
    punctuation_score * 0.3 +
    filler_score * 0.3
)

# Step 4: Vocabulary Diversity (0-1)
unique_words = len(set(words))
total_words = len(words)
ttr = unique_words / total_words if total_words > 0 else 0
vocabulary_diversity = min(1.0, ttr / 0.6)  # Normalize to typical range [0.4, 0.8]

# Step 5: Coherence Score (0-1)
transition_words = ['however', 'therefore', 'moreover', 'furthermore', 
                    'consequently', 'additionally', 'meanwhile']
transition_count = sum(1 for word in words if word in transition_words)
transition_score = min(1.0, transition_count / len(sentences)) if sentences else 0
base_coherence = 0.4

coherence_score = (
    transition_score * 0.6 +
    base_coherence * 0.4
)

# Step 6: Technical Terms Extraction
technical_terms = []
for keyword in TECHNICAL_KEYWORDS:
    if keyword.lower() in [w.lower() for w in words]:
        technical_terms.append(keyword)

# Step 7: Sentiment Analysis
positive_words = ['excited', 'passionate', 'excellent', 'great', 'confident']
negative_words = ['difficult', 'failed', 'problem', 'weak', 'uncertain']
positive_count = sum(1 for w in words if w in positive_words)
negative_count = sum(1 for w in words if w in negative_words)

if positive_count > negative_count:
    sentiment = "positive"
elif negative_count > positive_count:
    sentiment = "negative"
else:
    sentiment = "neutral"
```

**Output**: `TranscriptAnalysisResult` with clarity_score, vocabulary_diversity, coherence_score, technical_terms, word_count, sentiment

---

### **5. Role Matching Algorithm**

**Technology**: SentenceTransformers (all-MiniLM-L6-v2), scikit-learn

**Algorithm**:

```python
# Step 1: Gather Candidate Skills
candidate_skills = set()
if resume_analysis:
    candidate_skills.update([s.lower() for s in resume_analysis.skills])
    candidate_skills.update([t.lower() for t in resume_analysis.tools])
if transcript_analysis:
    candidate_skills.update([t.lower() for t in transcript_analysis.technical_terms])

# Step 2: Skill Match Percentage (50% weight)
required_skills = set([s.lower() for s in job_description.required_skills])
matching_skills = candidate_skills.intersection(required_skills)
skill_match_pct = (len(matching_skills) / len(required_skills) * 100) if required_skills else 50.0

# Step 3: Experience Match (20% weight)
candidate_years = resume_analysis.experience_years if resume_analysis else 0
required_years = job_description.experience_years or 0
experience_match = 100 if candidate_years >= required_years else 50

# Step 4: Semantic Similarity (30% weight)
# Encode job description
jd_text = f"{job_description.title}. {job_description.description}"
jd_embedding = model.encode(jd_text)

# Encode candidate profile
candidate_text = ""
if resume_analysis:
    candidate_text += extract_resume_summary(resume_analysis)[:500]
if transcript_analysis:
    candidate_text += transcript_analysis.text[:500]
candidate_embedding = model.encode(candidate_text)

# Compute cosine similarity
semantic_similarity = cosine_similarity(
    jd_embedding.reshape(1, -1),
    candidate_embedding.reshape(1, -1)
)[0][0]  # Range: [-1, 1], typically [0, 1] for similar texts

# Step 5: Overall Match Percentage
match_percentage = (
    skill_match_pct * 0.5 +           # 50% weight
    experience_match * 0.2 +          # 20% weight
    semantic_similarity * 100 * 0.3   # 30% weight
)

# Step 6: Identify Strengths & Gaps
strengths = []
if len(matching_skills) >= 5:
    strengths.append("Strong skill match")
if matching_skills.intersection(job_description.preferred_skills):
    strengths.append("Has preferred skills")

missing_skills = list(required_skills - candidate_skills)
gaps = []
if len(missing_skills) <= 3:
    gaps.append("Minor skill gaps")
else:
    gaps.append("Multiple skill gaps")
```

**Output**: `RoleMatchResult` with match_percentage, matching_skills, missing_skills, strengths, gaps

---

### **6. Soft Skills Analysis Algorithm**

**Technology**: Custom weighted combination

**Algorithm**:

```python
# Step 1: Communication Score (0-1)
if transcript_analysis:
    clarity = transcript_analysis.clarity_score
    vocabulary = transcript_analysis.vocabulary_diversity
    coherence = transcript_analysis.coherence_score
    word_count_score = min(1.0, transcript_analysis.word_count / 100)
    
    communication = (
        clarity * 0.35 +
        vocabulary * 0.25 +
        coherence * 0.3 +
        word_count_score * 0.1
    )
else:
    communication = 0.5  # Neutral if no transcript

# Step 2: Confidence Score (0-1)
confidence_scores = []
if video_analysis:
    confidence_scores.append(video_analysis.confidence_score)
    confidence_scores.append(video_analysis.eye_contact_score)
    confidence_scores.append(video_analysis.posture_score)

if transcript_analysis:
    sentiment_score = 0.7 if transcript_analysis.sentiment == "positive" else 0.5
    confidence_scores.append(sentiment_score)
    confidence_scores.append(transcript_analysis.clarity_score)

confidence = mean(confidence_scores) if confidence_scores else 0.5

# Step 3: Engagement Score (0-1)
if video_analysis:
    engagement = (
        video_analysis.expressiveness_score * 0.4 +
        video_analysis.gesture_score * 0.3 +
        video_analysis.eye_contact_score * 0.3
    )
else:
    engagement = 0.5

# Step 4: Professionalism Score (0-1)
professionalism_scores = []
if video_analysis:
    professionalism_scores.append(video_analysis.posture_score)
    gesture_appropriateness = 0.9 if 0.3 <= video_analysis.gesture_score <= 0.8 else 0.6
    professionalism_scores.append(gesture_appropriateness)

if transcript_analysis:
    tech_term_score = min(1.0, len(transcript_analysis.technical_terms) / 5)
    professionalism_scores.append(tech_term_score)
    professionalism_scores.append(transcript_analysis.coherence_score)
    word_count_score = min(1.0, transcript_analysis.word_count / 150)
    professionalism_scores.append(word_count_score)

professionalism = mean(professionalism_scores) if professionalism_scores else 0.5

# Step 5: Overall Soft Skills Score (0-1)
overall_soft_skills = (
    communication * 0.3 +
    confidence * 0.3 +
    engagement * 0.2 +
    professionalism * 0.2
)
```

**Output**: `SoftSkillIndex` with communication, confidence, engagement, professionalism, overall_score

---

## 🎯 Score Aggregation & Final Evaluation

### **Overall Score Calculation**

The final candidate score combines three major components with weighted aggregation:

```python
# Standard Mode (with video analysis)
overall_score = (
    role_match.match_percentage * 0.4 +           # 40% - Job fit
    soft_skill_index.overall_score * 100 * 0.3 +   # 30% - Interpersonal skills
    video_analysis.confidence_score * 100 * 0.3   # 30% - Presentation quality
)

# Accessibility Mode (no video analysis)
overall_score = (
    role_match.match_percentage * 0.6 +            # 60% - Increased weight
    soft_skill_index.overall_score * 100 * 0.4     # 40% - Increased weight
)
```

### **Recommendation Levels**

| Score Range | Recommendation | Interpretation |
|------------|----------------|----------------|
| 80-100 | **Highly Recommended** | Excellent candidate, strong match |
| 60-79 | **Recommended** | Good candidate, solid qualifications |
| 40-59 | **Consider with Reservations** | Potential but needs development |
| 0-39 | **Not Recommended** | Significant gaps or concerns |

### **Why These Weights?**

1. **Role Match (40%)**: Primary factor - technical fit is most critical
2. **Soft Skills (30%)**: Important for team collaboration and communication
3. **Video Confidence (30%)**: Presentation quality matters for client-facing roles

**Rationale**: Technical competency is weighted highest, but soft skills and presentation are essential for success in most roles.

---

## ✨ Key Features

### **1. Recruiter-Controlled Job Postings**
- Recruiters create and manage job postings from dashboard
- Candidates select from active postings (no manual entry)
- Consistent evaluation criteria per role
- Application tracking per job

### **2. Multi-Submission Tracking**
- Candidates can resubmit for same job
- Automatic version tracking (v1, v2, v3...)
- Improvement comparison between submissions
- Progress visualization with detailed metrics

### **3. Video Quality Pre-Check**
- Pre-submission quality validation
- Checks: resolution, duration, FPS, lighting, face detection
- Provides recommendations before evaluation
- Prevents poor evaluations due to technical issues

### **4. Comprehensive PDF Reports**
- Professional 2-3 page evaluation reports
- Detailed feedback sections (overall, technical, soft skills, video, role fit)
- 8 actionable recommendations
- Exportable for sharing and archiving

### **5. Modern UI/UX**
- Purple-cyan gradient theme
- Animated backgrounds and hover effects
- Glass morphism navigation
- Responsive design

---

## 📖 Usage Guide

### **For Recruiters**

1. **Create Job Posting**:
   - Navigate to Recruiter Dashboard
   - Click "Job Postings" tab
   - Click "Create New Job"
   - Fill in title, description, required/preferred skills, experience years
   - Set status to "Active"

2. **View Candidates**:
   - Switch to "Candidates" tab
   - See all evaluations with scores and recommendations
   - Click evaluation ID to view detailed report
   - Export PDF for sharing

### **For Candidates**

1. **Submit Application**:
   - Navigate to Candidate Page
   - Enter your name
   - Select job from dropdown
   - Upload video resume (MP4)
   - Upload resume (PDF/DOCX)
   - Click "Evaluate"

2. **View Results**:
   - See overall score and breakdown
   - Review detailed metrics
   - Check improvement comparison (if resubmitting)
   - Export PDF report

3. **Resubmit for Improvement**:
   - Use same name and job selection
   - System detects previous submission
   - Upload improved video/resume
   - See side-by-side comparison

---

## 🛠️ Technology Stack

### **Backend**
- **Framework**: FastAPI 0.104+
- **ML/AI Libraries**:
  - MediaPipe 0.10+ (video analysis)
  - OpenAI Whisper API (transcription)
  - spaCy 3.7+ (NLP)
  - SentenceTransformers (embeddings)
  - scikit-learn (similarity metrics)
- **Document Processing**: PyPDF2, python-docx
- **Visualization**: Matplotlib
- **PDF Generation**: ReportLab
- **Templating**: Jinja2

### **Frontend**
- **Framework**: React 18 + Vite
- **Styling**: TailwindCSS
- **Routing**: React Router DOM
- **HTTP Client**: Axios
- **Charts**: Recharts
- **File Upload**: React Dropzone

---

## ⚡ Performance & Limitations

### **Processing Time Estimates**

| Component | Typical Time | Optimization |
|-----------|-------------|--------------|
| Video Upload | 1-5s | Compression, streaming |
| Video Processing | 10-30s | Frame sampling (every 5th), GPU |
| Audio Transcription | 5-15s | API latency |
| Resume Parsing | 1-3s | Text length |
| Role Matching | 2-5s | Embedding cache |
| Report Generation | 3-7s | Chart rendering |
| **Total** | **25-70s** | Parallel processing |

### **Known Limitations**

#### **1. Eye Tracking Limitations**
- Assumes constant eye contact is ideal (unrealistic)
- Natural eye movement while thinking is penalized
- Cultural differences in eye contact norms not accounted for
- May disadvantage neurodivergent candidates

**Mitigation**: Temporal smoothing, relaxed thresholds, confidence intervals, contextual notes

#### **2. Posture Analysis Limitations**
- Expects rigid posture (biomechanically unrealistic)
- Natural movement and shifting penalized
- Body diversity and physical conditions not considered
- Camera angle and furniture affect measurements

**Mitigation**: Windowed averaging, duration-based adjustments, measurement notes

#### **3. Gesture Analysis Limitations**
- Culturally biased gesture expectations
- Camera framing affects hand visibility
- Context-dependent (formal vs. casual)

**Mitigation**: Appropriate range (0.3-0.8), not overly strict

### **Ethical Considerations**

⚠️ **Important**: This system should be used as a **coaching tool** for candidates, not a **screening tool** for final hiring decisions.

**Best Practices**:
- ✅ Provide human review of all automated decisions
- ✅ Use for interview preparation and feedback
- ✅ Supplement (not replace) recruiter judgment
- ✅ Document limitations in candidate-facing materials
- ❌ Do NOT make final hiring decisions solely based on scores
- ❌ Do NOT compare candidates from different cultural backgrounds directly

---

## 📊 Evaluation Parameters Reference

### **Video Analysis**
- **Eye Contact Range**: 0.35-0.65 (normalized x-coordinate)
- **Posture Tolerance**: Shoulder difference < 0.1 (normalized)
- **Gesture Optimal Range**: 0.3-0.8
- **Frame Sampling**: Every 5th frame
- **Temporal Window**: 10 frames for smoothing

### **NLP Analysis**
- **Optimal Sentence Length**: 15 words
- **Vocabulary TTR Range**: 0.4-0.8 (normalized to 0.6)
- **Filler Word Penalty**: 0.05 per occurrence
- **Transition Word Weight**: 60% of coherence

### **Role Matching**
- **Skill Match Weight**: 50%
- **Experience Match Weight**: 20%
- **Semantic Similarity Weight**: 30%
- **Embedding Model**: all-MiniLM-L6-v2 (384 dimensions)

### **Soft Skills**
- **Communication**: Clarity (35%) + Vocabulary (25%) + Coherence (30%) + Word Count (10%)
- **Confidence**: Average of video scores + sentiment + clarity
- **Engagement**: Expressiveness (40%) + Gestures (30%) + Eye Contact (30%)
- **Professionalism**: Average of posture, gestures, tech terms, coherence, length

---

## 🎓 Algorithm Summary for Presentation

### **Why This Approach Works**

1. **Multi-Modal Analysis**: Combines visual, audio, and textual data for comprehensive assessment
2. **Weighted Aggregation**: Prioritizes role fit (40%) while valuing soft skills (30%) and presentation (30%)
3. **Temporal Smoothing**: Reduces noise from momentary variations in video metrics
4. **Semantic Understanding**: Uses embeddings to capture meaning beyond keyword matching
5. **Configurable Thresholds**: Easy to adjust parameters for different roles or requirements

### **Key Innovations**

- **Temporal Window Smoothing**: Averages metrics over time windows instead of per-frame analysis
- **Confidence Intervals**: Reports uncertainty ranges for transparency
- **Duration-Based Adjustments**: Longer videos get slight bonuses (more comprehensive responses)
- **Multi-Source Confidence**: Combines video, transcript, and sentiment for robust confidence scoring
- **Semantic Role Matching**: Goes beyond keyword matching to understand job-candidate fit

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Support

For questions or issues:
- Create GitHub issue
- Email: support@visumeai.example.com
- Documentation: https://docs.visumeai.example.com

---

**Version**: 2.3  
**Last Updated**: October 2025  
**Maintainer**: VisumeAI Team
