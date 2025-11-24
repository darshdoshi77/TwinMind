# Testing Different Media Types

## ✅ What Works & How to Test

### 1. **Text Notes** ✅ Working
**How to test:**
- Click "Add Content" → "Text" tab
- Type any text content
- Save and query it

---

### 2. **Web Articles** ✅ Ready to Test
**How to test:**
- Click "Add Content" → "Web" tab
- Paste a URL (e.g., `https://en.wikipedia.org/wiki/Machine_learning`)
- Click "Ingest Web Content"
- Wait 5-10 seconds
- Ask: "What did the article say about [topic]?"

**Good test URLs:**
- `https://en.wikipedia.org/wiki/Artificial_intelligence`
- `https://en.wikipedia.org/wiki/Python_(programming_language)`
- Any news article or blog post

---

### 3. **Documents** ✅ Ready to Test
**Supported formats:**
- PDF (`.pdf`)
- Markdown (`.md`)
- Text files (`.txt`)
- Word documents (`.docx`)

**How to test:**
- Click "Add Content" → "File" tab
- Upload a PDF or text document
- Wait for processing
- Query about the document content

**Example queries after upload:**
- "Summarize the document I just uploaded"
- "What are the main points?"
- "What did the PDF say about [topic]?"

---

### 4. **Audio Files** ✅ Ready to Test
**Supported formats:**
- `.mp3`
- `.m4a`
- `.wav`
- `.mp4` (video with audio)

**How to test:**
1. Get an audio file (meeting recording, podcast, voice memo)
2. Click "Add Content" → "File" tab
3. Upload the audio file
4. Wait 30 seconds - 5 minutes (depends on file length)
   - Processing includes transcription via Whisper API
5. Query about the audio:
   - "What was discussed in the meeting?"
   - "Summarize the audio I uploaded"
   - "What were the key points?"

**Note:** Audio transcription uses OpenAI Whisper API and may take time.

---

### 5. **Images** ⚠️ Basic Support
**Current status:** Images can be stored, but full search requires:
- OCR text extraction (manual setup needed)
- Or user-provided captions/descriptions

**To test:**
- Images can be uploaded but may not be fully searchable yet
- For MVP, focus on text-based content (audio transcripts, documents, web)

---

## 🎯 Recommended Test Flow

### Test 1: Web Content
```
1. Add web article about "quantum computing"
2. Wait 5 seconds
3. Ask: "What is quantum computing?"
4. ✅ Should reference the article
```

### Test 2: Multiple Sources
```
1. Add text: "I love Python"
2. Add web article about Python
3. Ask: "What programming language do I like?"
4. ✅ Should synthesize from both sources
```

### Test 3: Temporal Query
```
1. Add content today
2. Wait a moment
3. Ask: "What did I add today?"
4. ✅ Should show today's content
```

### Test 4: Audio (If You Have One)
```
1. Upload a short audio file (1-2 minutes)
2. Wait for transcription
3. Ask: "What was said in the audio?"
4. ✅ Should reference transcript
```

---

## 📝 Tips

- **Wait after uploading**: Processing takes 3-10 seconds for text/web, longer for audio
- **Start simple**: Try text and web first (they're fastest)
- **Audio takes time**: Transcription can take 1-5 minutes depending on length
- **Query naturally**: Ask questions as you would ask a person

---

## 🎉 What to Try Next

1. **Multiple content types** - Mix text, web, and documents
2. **Temporal queries** - "What did I add this week?"
3. **Complex questions** - "Compare the articles I saved about AI"
4. **Audio transcription** - Upload a short meeting recording

Enjoy testing! 🚀

