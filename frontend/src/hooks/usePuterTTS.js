import { useState, useEffect, useCallback, useRef } from 'react';

const usePuterTTS = () => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const puterRef = useRef(null);
  const currentUtteranceRef = useRef(null);
  const audioRef = useRef(null);

  // Load Puter.js from CDN
  useEffect(() => {
    const loadPuterJS = async () => {
      // Check if already loaded
      if (window.puter) {
        puterRef.current = window.puter;
        setIsLoaded(true);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        // Create script element
        const script = document.createElement('script');
        script.src = 'https://js.puter.com/v2/';
        script.async = true;
        script.crossOrigin = 'anonymous';
        
        // Wait for script to load
        await new Promise((resolve, reject) => {
          script.onload = resolve;
          script.onerror = () => reject(new Error('Failed to load Puter.js from CDN'));
          document.head.appendChild(script);
        });

        // Wait for puter to be available
        let attempts = 0;
        const maxAttempts = 50; // 5 seconds max wait
        
        while (!window.puter && attempts < maxAttempts) {
          await new Promise(resolve => setTimeout(resolve, 100));
          attempts++;
        }

        if (!window.puter) {
          throw new Error('Puter.js loaded but puter object not available');
        }

        puterRef.current = window.puter;
        setIsLoaded(true);
        console.log('✅ Puter.js loaded successfully');

      } catch (err) {
        setError(`Failed to load Puter.js: ${err.message}`);
        console.error('❌ Puter.js loading error:', err);
        
        // Fallback: Set up Web Speech API only
        if (window.speechSynthesis) {
          console.log('🔄 Falling back to Web Speech API');
          setIsLoaded(true);
        }
      } finally {
        setIsLoading(false);
      }
    };

    loadPuterJS();

    // Cleanup function
    return () => {
      stop();
    };
  }, []);

  // Speak function using Puter.js TTS or Web Speech API fallback
  const speak = useCallback(async (text, options = {}) => {
    if (!text || typeof text !== 'string') {
      throw new Error('Text must be a non-empty string');
    }

    // Stop any current speech
    stop();

    try {
      setIsSpeaking(true);
      setError(null);

      // Default options
      const ttsOptions = {
        voice: options.voice || 'en-US-Standard-A',
        rate: options.rate || 1.0,
        pitch: options.pitch || 1.0,
        volume: options.volume || 1.0,
        format: options.format || 'mp3',
        ...options
      };

      // Try Puter TTS first if available
      if (puterRef.current?.ai?.txt2speech) {
        try {
          console.log('🤖 Using Puter.js TTS');
          
          const audioData = await puterRef.current.ai.txt2speech(text, {
            voice: ttsOptions.voice,
            speed: ttsOptions.rate,
            pitch: ttsOptions.pitch,
            format: ttsOptions.format
          });
          
          // Create audio element and play
          const audio = new Audio();
          audioRef.current = audio;
          
          // Handle different audio data formats
          if (audioData instanceof ArrayBuffer) {
            const blob = new Blob([audioData], { type: `audio/${ttsOptions.format}` });
            audio.src = URL.createObjectURL(blob);
          } else if (typeof audioData === 'string') {
            // Assume it's a data URL or regular URL
            audio.src = audioData;
          } else {
            throw new Error('Unsupported audio data format from Puter TTS');
          }
          
          audio.volume = ttsOptions.volume;
          
          audio.onended = () => {
            setIsSpeaking(false);
            if (audio.src.startsWith('blob:')) {
              URL.revokeObjectURL(audio.src);
            }
          };
          
          audio.onerror = (event) => {
            setIsSpeaking(false);
            setError('Error playing generated audio');
            console.error('Audio playback error:', event);
          };
          
          await audio.play();
          return;
          
        } catch (puterError) {
          console.warn('Puter TTS failed, falling back to Web Speech API:', puterError);
        }
      }

      // Fallback to Web Speech API
      console.log('🎤 Using Web Speech API fallback');
      
      if (!window.speechSynthesis) {
        throw new Error('Neither Puter TTS nor Web Speech API is available');
      }

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = Math.max(0.1, Math.min(10, ttsOptions.rate));
      utterance.pitch = Math.max(0, Math.min(2, ttsOptions.pitch));
      utterance.volume = Math.max(0, Math.min(1, ttsOptions.volume));
      
      // Set voice if specified
      if (ttsOptions.voice && typeof ttsOptions.voice === 'string') {
        const voices = speechSynthesis.getVoices();
        const selectedVoice = voices.find(voice => 
          voice.lang.includes(ttsOptions.voice) || 
          voice.name.includes(ttsOptions.voice) ||
          voice.voiceURI.includes(ttsOptions.voice)
        );
        if (selectedVoice) {
          utterance.voice = selectedVoice;
        }
      }

      utterance.onstart = () => {
        console.log('🔊 Speech synthesis started');
      };

      utterance.onend = () => {
        setIsSpeaking(false);
        console.log('✅ Speech synthesis completed');
      };
      
      utterance.onerror = (event) => {
        setIsSpeaking(false);
        setError(`Speech synthesis error: ${event.error}`);
        console.error('Speech synthesis error:', event);
      };

      currentUtteranceRef.current = utterance;
      speechSynthesis.speak(utterance);

    } catch (err) {
      setIsSpeaking(false);
      setError(`TTS error: ${err.message}`);
      console.error('TTS error:', err);
      throw err;
    }
  }, []);

  // Stop speaking
  const stop = useCallback(() => {
    try {
      // Stop Web Speech API
      if (window.speechSynthesis && currentUtteranceRef.current) {
        window.speechSynthesis.cancel();
        currentUtteranceRef.current = null;
      }

      // Stop audio playback
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
        if (audioRef.current.src.startsWith('blob:')) {
          URL.revokeObjectURL(audioRef.current.src);
        }
        audioRef.current = null;
      }

      setIsSpeaking(false);
    } catch (err) {
      console.error('Error stopping TTS:', err);
    }
  }, []);

  // Pause speaking (Web Speech API only)
  const pause = useCallback(() => {
    try {
      if (window.speechSynthesis && isSpeaking) {
        window.speechSynthesis.pause();
      }
      if (audioRef.current && !audioRef.current.paused) {
        audioRef.current.pause();
      }
    } catch (err) {
      console.error('Error pausing TTS:', err);
    }
  }, [isSpeaking]);

  // Resume speaking (Web Speech API only)
  const resume = useCallback(() => {
    try {
      if (window.speechSynthesis) {
        window.speechSynthesis.resume();
      }
      if (audioRef.current && audioRef.current.paused) {
        audioRef.current.play();
      }
    } catch (err) {
      console.error('Error resuming TTS:', err);
    }
  }, []);

  // Get available voices
  const getVoices = useCallback(() => {
    if (!window.speechSynthesis) {
      return [];
    }
    return speechSynthesis.getVoices();
  }, []);

  // Check if TTS is supported
  const isSupported = isLoaded || !!window.speechSynthesis;

  return {
    // State
    isLoaded,
    isLoading,
    error,
    isSpeaking,
    isSupported,
    
    // Actions
    speak,
    stop,
    pause,
    resume,
    
    // Utilities
    getVoices,
    
    // References for advanced usage
    puter: puterRef.current,
    speechSynthesis: window.speechSynthesis
  };
};

export default usePuterTTS;
