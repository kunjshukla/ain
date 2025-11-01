import { useState, useCallback, useEffect } from 'react';
import useSpeechRecognition from './useSpeechRecognition';
import usePuterTTS from './usePuterTTS';

const useVoiceInteraction = () => {
  const [isActive, setIsActive] = useState(false);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [autoStop, setAutoStop] = useState(true);
  const [autoStopDelay, setAutoStopDelay] = useState(3000); // 3 seconds of silence
  
  const speechRecognition = useSpeechRecognition();
  const tts = usePuterTTS();
  
  const [silenceTimer, setSilenceTimer] = useState(null);

  // Auto-stop listening after silence
  useEffect(() => {
    if (autoStop && speechRecognition.isListening) {
      // Clear existing timer
      if (silenceTimer) {
        clearTimeout(silenceTimer);
      }
      
      // Set new timer if there's transcript content
      if (speechRecognition.transcript || speechRecognition.interimTranscript) {
        const timer = setTimeout(() => {
          if (speechRecognition.isListening) {
            speechRecognition.stopListening();
            setIsActive(false);
          }
        }, autoStopDelay);
        
        setSilenceTimer(timer);
      }
    }
    
    return () => {
      if (silenceTimer) {
        clearTimeout(silenceTimer);
      }
    };
  }, [speechRecognition.transcript, speechRecognition.interimTranscript, speechRecognition.isListening, autoStop, autoStopDelay, silenceTimer]);

  // Start voice interaction
  const startVoiceInteraction = useCallback((options = {}) => {
    if (!speechRecognition.browserSupportsSpeechRecognition) {
      throw new Error('Speech recognition not supported');
    }
    
    // Stop any current TTS
    tts.stop();
    
    // Start listening
    speechRecognition.startListening({
      continuous: true,
      resetTranscript: true,
      ...options
    });
    
    setIsActive(true);
  }, [speechRecognition, tts]);

  // Stop voice interaction
  const stopVoiceInteraction = useCallback(() => {
    speechRecognition.stopListening();
    tts.stop();
    setIsActive(false);
    
    if (silenceTimer) {
      clearTimeout(silenceTimer);
      setSilenceTimer(null);
    }
  }, [speechRecognition, tts, silenceTimer]);

  // Speak response and optionally continue listening
  const speakAndListen = useCallback(async (text, options = {}) => {
    const { continueListening = true, ttsOptions = {}, listeningOptions = {} } = options;
    
    try {
      // Stop current listening
      if (speechRecognition.isListening) {
        speechRecognition.stopListening();
      }
      
      // Speak the response
      await tts.speak(text, ttsOptions);
      
      // Continue listening if requested
      if (continueListening && isActive) {
        // Small delay to avoid picking up the TTS audio
        setTimeout(() => {
          speechRecognition.startListening({
            resetTranscript: true,
            ...listeningOptions
          });
        }, 500);
      }
      
    } catch (error) {
      console.error('Error in speakAndListen:', error);
      throw error;
    }
  }, [speechRecognition, tts, isActive]);

  // Add message to conversation history
  const addToHistory = useCallback((message, type = 'user') => {
    const entry = {
      id: Date.now(),
      message,
      type, // 'user' | 'assistant' | 'system'
      timestamp: new Date().toISOString()
    };
    
    setConversationHistory(prev => [...prev, entry]);
    return entry;
  }, []);

  // Clear conversation history
  const clearHistory = useCallback(() => {
    setConversationHistory([]);
  }, []);

  // Get final transcript and add to history
  const finalizeSpeech = useCallback(() => {
    const finalText = speechRecognition.getFullTranscript().trim();
    
    if (finalText) {
      addToHistory(finalText, 'user');
      speechRecognition.resetTranscript();
      return finalText;
    }
    
    return null;
  }, [speechRecognition, addToHistory]);

  // Toggle listening state
  const toggleListening = useCallback(() => {
    if (speechRecognition.isListening) {
      stopVoiceInteraction();
    } else {
      startVoiceInteraction();
    }
  }, [speechRecognition.isListening, startVoiceInteraction, stopVoiceInteraction]);

  // Configuration methods
  const setAutoStopConfig = useCallback((enabled, delay = 3000) => {
    setAutoStop(enabled);
    setAutoStopDelay(delay);
  }, []);

  // Get current status
  const getStatus = useCallback(() => {
    return {
      isListening: speechRecognition.isListening,
      isSpeaking: tts.isSpeaking,
      isActive,
      hasTranscript: !!(speechRecognition.transcript || speechRecognition.interimTranscript),
      canStart: speechRecognition.browserSupportsSpeechRecognition && tts.isSupported,
      error: speechRecognition.error || tts.error
    };
  }, [speechRecognition, tts, isActive]);

  return {
    // State
    isActive,
    conversationHistory,
    
    // Speech Recognition
    transcript: speechRecognition.transcript,
    interimTranscript: speechRecognition.interimTranscript,
    isListening: speechRecognition.isListening,
    
    // Text-to-Speech
    isSpeaking: tts.isSpeaking,
    
    // Errors and Support
    speechError: speechRecognition.error,
    ttsError: tts.error,
    isSupported: speechRecognition.browserSupportsSpeechRecognition && tts.isSupported,
    
    // Actions
    startVoiceInteraction,
    stopVoiceInteraction,
    toggleListening,
    speakAndListen,
    finalizeSpeech,
    
    // History Management
    addToHistory,
    clearHistory,
    
    // Configuration
    setAutoStopConfig,
    
    // Utilities
    getStatus,
    
    // Individual hook access for advanced usage
    speechRecognition,
    tts
  };
};

export default useVoiceInteraction;
