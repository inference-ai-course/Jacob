from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import Response
from app.asr import ASR
from app.llm import LLM_Agent
from app.tts import TTS_Engine
from app.memory import ConversationMemory
import os
import time

app = FastAPI(title="Voice Agent")

# Initialize components
asr = ASR()
llm = LLM_Agent()
tts = TTS_Engine()
memory = ConversationMemory()

@app.post("/converse")
async def converse(audio: UploadFile):
    try:
        # 1. Transcribe audio
        start_time = time.time()
        audio_bytes = await audio.read()
        transcription = asr.transcribe(audio_bytes)
        transcribe_time = time.time() - start_time
        
        if not transcription:
            return {"text": "", "audio": b"", "transcription_time": transcribe_time}
        
        # 2. Generate response with conversation history
        start_llm = time.time()
        prompt = memory.get_prompt(transcription)
        response_text = llm.generate(prompt)
        llm_time = time.time() - start_llm
        
        # Update memory
        memory.add_message("user", transcription)
        memory.add_message("assistant", response_text)
        
        # 3. Convert response to speech
        start_tts = time.time()
        response_audio = tts.synthesize(response_text)
        tts_time = time.time() - start_tts
        
        return {
            "text": response_text,
            "audio": response_audio,
            "transcription_time": transcribe_time,
            "llm_time": llm_time,
            "tts_time": tts_time,
            "total_time": time.time() - start_time
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
async def reset_conversation():
    """Reset the conversation history"""
    memory.clear()
    return {"status": "conversation reset"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}