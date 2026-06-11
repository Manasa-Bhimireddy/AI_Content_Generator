# 🚀 AI Content Generator for Blogs and Social Media

An AI-powered content generation platform built using **Flask, FAISS Vector Database, Sentence Transformers, and Groq Large Language Models (LLMs)**. The application generates high-quality, context-aware content for blogs and social media platforms such as Instagram, LinkedIn, and Twitter/X based on user-provided topics and tone preferences.

---

## 📌 Features

- ✨ AI-powered content generation
- 🔍 Retrieval-Augmented Generation (RAG)
- 📚 Semantic similarity search using FAISS
- 🤖 Content generation with Groq LLM
- 📝 Blog and social media content creation
- 📖 Content history tracking
- ⚡ Fast and efficient response generation
- 🎨 Responsive and user-friendly interface

---

## 🛠️ Tech Stack

### Backend
- Python
- Flask

### AI & NLP
- Groq API
- Sentence Transformers
- Retrieval-Augmented Generation (RAG)

### Database
- FAISS Vector Database

### Frontend
- HTML
- CSS
- JavaScript
- Jinja2 Templates

### Storage
- Pickle (.pkl)
- FAISS Binary Index

---

## 📂 Project Structure

```text
AI_content_Generator/
│
├── app.py
├── requirement.txt
├── .env
│
├── vector_store/
│   ├── faiss_index.bin
│   └── stored_texts.pkl
│
├── utils/
│   ├── embeddings.py
│   ├── vector_db.py
│   └── groq_generator.py
│
├── templates/
│   ├── layout.html
│   ├── index.html
│   └── history.html
│
└── static/
    ├── style.css
    └── script.js
```

---

## ⚙️ How It Works

### 1. User Input
The user enters:
- Topic
- Content Type
- Tone Preference

### 2. Embedding Generation
Sentence Transformers convert the input into vector embeddings.

### 3. Similarity Search
FAISS performs semantic similarity search on previously generated content.

### 4. Context Retrieval
Relevant content is retrieved and used as context.

### 5. Content Generation
Groq LLM generates high-quality, personalized content.

### 6. Storage
Generated content is:
- Embedded using Sentence Transformers
- Stored in the FAISS database
- Saved for future retrieval

---

## 🚀 Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/AI_content_Generator.git
cd AI_content_Generator
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirement.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the root directory and add:

```env
GROQ_API_KEY=your_api_key_here
```

---

## ▶️ Run the Application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

---

## 📸 Use Cases

- Blog Writing
- LinkedIn Posts
- Instagram Captions
- Twitter/X Content
- Marketing Content
- Product Descriptions
- SEO Content Generation

---

## 🎯 Future Enhancements

- Multi-language Support
- User Authentication
- PDF/Word Export
- Cloud Database Integration
- Content Scheduling
- AI Analytics Dashboard

---

## 👨‍💻 Author

**Bhimireddy Manasa**

 Project – AI Content Generator using Flask, FAISS, Sentence Transformers, and Groq LLM.

---

## ⭐ Support

If you like this project, consider giving it a **Star ⭐** on GitHub.

---

