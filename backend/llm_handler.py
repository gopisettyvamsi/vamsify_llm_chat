import os
import urllib.request
from pathlib import Path
from typing import Iterator
from llama_cpp import Llama
from config import (
    MODEL_PATH, MODEL_URL, MODEL_NAME,
    N_CTX, N_THREADS, N_GPU_LAYERS,
    MAX_TOKENS, TEMPERATURE
)


class LLMHandler:
    """Handles LLM model loading and inference."""
    
    def __init__(self):
        self.model = None
        self._ensure_model_exists()
        self._load_model()
    
    def _ensure_model_exists(self) -> None:
        """Download the model if it doesn't exist locally."""
        if MODEL_PATH.exists():
            print(f"✓ Model found: {MODEL_PATH}")
            return
        
        print(f"Model not found. Downloading {MODEL_NAME}...")
        print(f"URL: {MODEL_URL}")
        print(f"Destination: {MODEL_PATH}")
        print("This may take several minutes (800MB-2GB)...")
        
        try:
            # Download with progress
            def report_progress(block_num, block_size, total_size):
                downloaded = block_num * block_size
                percent = min(downloaded * 100 / total_size, 100)
                print(f"\rDownloading: {percent:.1f}%", end="", flush=True)
            
            urllib.request.urlretrieve(
                MODEL_URL,
                MODEL_PATH,
                reporthook=report_progress
            )
            print("\n✓ Download complete!")
        except Exception as e:
            print(f"\n✗ Download failed: {e}")
            raise
    
    def _load_model(self) -> None:
        """Load the LLM model into memory."""
        print(f"Loading model: {MODEL_NAME}...")
        try:
            self.model = Llama(
                model_path=str(MODEL_PATH),
                n_ctx=N_CTX,
                n_threads=N_THREADS,
                n_gpu_layers=N_GPU_LAYERS,
                verbose=False
            )
            print("✓ Model loaded successfully!")
        except Exception as e:
            print(f"✗ Failed to load model: {e}")
            raise
    
    def generate(self, prompt: str, stream: bool = False) -> str | Iterator[str]:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The input prompt
            stream: If True, return an iterator for streaming responses
        
        Returns:
            Complete response string or iterator of response chunks
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        try:
            response = self.model(
                prompt,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                stop=["User:", "System:"],
                stream=stream,
                echo=False
            )
            
            if stream:
                return self._stream_response(response)
            else:
                return response["choices"][0]["text"].strip()
        
        except Exception as e:
            print(f"Generation error: {e}")
            raise
    
    def _stream_response(self, response_iterator) -> Iterator[str]:
        """Process streaming response from the model."""
        for chunk in response_iterator:
            text = chunk["choices"][0]["text"]
            if text:
                yield text
    
    def is_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self.model is not None
