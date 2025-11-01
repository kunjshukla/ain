import { useState, useEffect, useCallback } from 'react';

/**
 * Minimal Puter.js TTS Hook
 * Loads Puter.js from CDN and provides simple speak function
 */
const useSimplePuterTTS = () => {
  const [isReady, setIsReady] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [error, setError] = useState(null);

  // Load Puter.js on mount
  useEffect(() => {
    const loadPuter = async () => {
      try {
        // Skip if already loaded
        if (window.puter) {
          setIsReady(true);
          return;
        }

        // Load script
        const script = document.createElement('script');
        script.src = 'https://js.puter.com/v2/';
        script.async = true;
        
        script.onload = () => {
          // Wait for puter object to be available
          const checkPuter = () => {
            if (window.puter) {
              setIsReady(true);
            } else {
              setTimeout(checkPuter, 100);
            }
          };
          checkPuter();
        };
        
        script.onerror = () => {
          setError('Failed to load Puter.js');
          // Fallback: enable Web Speech API
          if (window.speechSynthesis) {
            setIsReady(true);
          }
        };

        document.head.appendChild(script);
        
      } catch (err) {
        setError(err.message);
      }
    };

    loadPuter();
  }, []);

  // Simple speak function
  const speak = useCallback(async (text) => {
    if (!text) return;
    
    setIsSpeaking(true);
    setError(null);

    try {
      // Try Puter.js first
      if (window.puter?.ai?.txt2speech) {
        const audioData = await window.puter.ai.txt2speech(text);
        const audio = new Audio();
        const blob = new Blob([audioData], { type: 'audio/mp3' });
        audio.src = URL.createObjectURL(blob);
        
        audio.onended = () => {
          setIsSpeaking(false);
          URL.revokeObjectURL(audio.src);
        };
        
        await audio.play();
      } 
      // Fallback to Web Speech API
      else if (window.speechSynthesis) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.onend = () => setIsSpeaking(false);
        speechSynthesis.speak(utterance);
      } 
      else {
        throw new Error('No TTS capability available');
      }
    } catch (err) {
      setError(err.message);
      setIsSpeaking(false);
    }
  }, []);

  // Stop speaking
  const stop = useCallback(() => {
    if (window.speechSynthesis) {
      speechSynthesis.cancel();
    }
    setIsSpeaking(false);
  }, []);

  return {
    speak,
    stop,
    isReady,
    isSpeaking,
    error
  };
};

export default useSimplePuterTTS;
