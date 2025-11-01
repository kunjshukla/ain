import { useState, useEffect, useCallback, useRef } from 'react';

const useSpeechRecognition = () => {
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState(null);
  const [browserSupportsSpeechRecognition, setBrowserSupportsSpeechRecognition] = useState(false);
  
  const recognitionRef = useRef(null);
  const finalTranscriptRef = useRef('');

  // Initialize speech recognition
  useEffect(() => {
    // Check for browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      setError('Speech recognition is not supported in this browser');
      setBrowserSupportsSpeechRecognition(false);
      return;
    }

    setBrowserSupportsSpeechRecognition(true);

    // Create recognition instance
    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;

    // Configure recognition settings
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;

    // Event handlers
    recognition.onstart = () => {
      setIsListening(true);
      setError(null);
      console.log('🎤 Speech recognition started');
    };

    recognition.onresult = (event) => {
      let interimTranscript = '';
      let finalTranscript = finalTranscriptRef.current;

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        const transcript = result[0].transcript;

        if (result.isFinal) {
          finalTranscript += transcript + ' ';
        } else {
          interimTranscript += transcript;
        }
      }

      finalTranscriptRef.current = finalTranscript;
      setTranscript(finalTranscript.trim());
      setInterimTranscript(interimTranscript);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      
      let errorMessage = 'Speech recognition error';
      switch (event.error) {
        case 'network':
          errorMessage = 'Network error - check your internet connection';
          break;
        case 'not-allowed':
          errorMessage = 'Microphone access denied. Please allow microphone access.';
          break;
        case 'no-speech':
          errorMessage = 'No speech detected. Please try speaking again.';
          break;
        case 'audio-capture':
          errorMessage = 'Audio capture failed. Check your microphone.';
          break;
        case 'service-not-allowed':
          errorMessage = 'Speech recognition service not allowed';
          break;
        default:
          errorMessage = `Speech recognition error: ${event.error}`;
      }
      
      setError(errorMessage);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
      setInterimTranscript('');
      console.log('🛑 Speech recognition ended');
    };

    // Cleanup function
    return () => {
      if (recognition) {
        recognition.stop();
      }
    };
  }, []);

  // Start listening
  const startListening = useCallback((options = {}) => {
    if (!recognitionRef.current) {
      setError('Speech recognition not initialized');
      return;
    }

    if (isListening) {
      console.warn('Speech recognition is already active');
      return;
    }

    try {
      // Configure language if provided
      if (options.language) {
        recognitionRef.current.lang = options.language;
      }

      // Configure continuous mode
      if (typeof options.continuous === 'boolean') {
        recognitionRef.current.continuous = options.continuous;
      }

      // Reset transcript if requested
      if (options.resetTranscript !== false) {
        finalTranscriptRef.current = '';
        setTranscript('');
        setInterimTranscript('');
      }

      setError(null);
      recognitionRef.current.start();
    } catch (err) {
      setError(`Failed to start speech recognition: ${err.message}`);
      console.error('Start listening error:', err);
    }
  }, [isListening]);

  // Stop listening
  const stopListening = useCallback(() => {
    if (!recognitionRef.current) {
      return;
    }

    if (!isListening) {
      console.warn('Speech recognition is not active');
      return;
    }

    try {
      recognitionRef.current.stop();
    } catch (err) {
      console.error('Stop listening error:', err);
      setError(`Failed to stop speech recognition: ${err.message}`);
    }
  }, [isListening]);

  // Reset transcript
  const resetTranscript = useCallback(() => {
    finalTranscriptRef.current = '';
    setTranscript('');
    setInterimTranscript('');
  }, []);

  // Abort recognition (immediately stop)
  const abortListening = useCallback(() => {
    if (!recognitionRef.current) {
      return;
    }

    try {
      recognitionRef.current.abort();
      setIsListening(false);
      setInterimTranscript('');
    } catch (err) {
      console.error('Abort listening error:', err);
    }
  }, []);

  // Get current full transcript (final + interim)
  const getFullTranscript = useCallback(() => {
    return transcript + (interimTranscript ? ' ' + interimTranscript : '');
  }, [transcript, interimTranscript]);

  // Check if microphone is available
  const checkMicrophonePermission = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => track.stop());
      return true;
    } catch (err) {
      setError('Microphone access denied or unavailable');
      return false;
    }
  }, []);

  return {
    // State
    transcript,
    interimTranscript,
    isListening,
    error,
    browserSupportsSpeechRecognition,
    
    // Actions
    startListening,
    stopListening,
    resetTranscript,
    abortListening,
    
    // Utilities
    getFullTranscript,
    checkMicrophonePermission,
    
    // Recognition instance (for advanced usage)
    recognition: recognitionRef.current
  };
};

export default useSpeechRecognition;
