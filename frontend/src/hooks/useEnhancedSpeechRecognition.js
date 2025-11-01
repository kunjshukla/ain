import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * Enhanced Speech Recognition Hook
 * Uses multiple STT providers for better accuracy
 */
const useEnhancedSpeechRecognition = () => {
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [confidence, setConfidence] = useState(0);
  const [serviceUsed, setServiceUsed] = useState('');
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);
  const processingTimeoutRef = useRef(null);

  // Check browser support for MediaRecorder
  const browserSupportsRecording = useCallback(() => {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia && window.MediaRecorder);
  }, []);

  // Start recording audio
  const startListening = useCallback(async () => {
    if (!browserSupportsRecording()) {
      setError('Audio recording is not supported in this browser');
      return;
    }

    try {
      setError(null);
      setIsListening(true);
      setTranscript('');
      setInterimTranscript('Listening...');
      audioChunksRef.current = [];

      // Get audio stream
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 16000,  // Optimal for STT
          channelCount: 1     // Mono audio
        }
      });

      streamRef.current = stream;

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'  // Good compression and quality
      });

      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        setIsListening(false);
        setIsProcessing(true);
        setInterimTranscript('Processing...');

        try {
          await processAudioChunks();
        } catch (error) {
          console.error('Error processing audio:', error);
          setError(`Processing failed: ${error.message}`);
          setIsProcessing(false);
          setInterimTranscript('');
        }
      };

      // Start recording
      mediaRecorder.start(1000); // Collect data every 1 second
      console.log('🎤 Recording started');

    } catch (error) {
      console.error('Error starting recording:', error);
      setError(`Failed to start recording: ${error.message}`);
      setIsListening(false);
      setInterimTranscript('');
    }
  }, []);

  // Stop recording
  const stopListening = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }

    // Set timeout for processing
    processingTimeoutRef.current = setTimeout(() => {
      if (isProcessing) {
        setError('Processing timeout - please try again');
        setIsProcessing(false);
        setInterimTranscript('');
      }
    }, 15000); // 15 second timeout
  }, [isProcessing]);

  // Process recorded audio chunks
  const processAudioChunks = useCallback(async () => {
    if (audioChunksRef.current.length === 0) {
      setError('No audio data recorded');
      setIsProcessing(false);
      setInterimTranscript('');
      return;
    }

    try {
      // Create audio blob
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      
      // Convert to WAV format for better STT compatibility
      const wavBlob = await convertToWav(audioBlob);
      
      // Send to enhanced STT endpoint
      const result = await sendToSTTService(wavBlob);
      
      if (result.success && result.text.trim()) {
        setTranscript(result.text.trim());
        setConfidence(result.confidence || 0);
        setServiceUsed(result.service_used || 'unknown');
        setError(null);
        
        console.log(`✅ STT Success (${result.service_used}): "${result.text}" (confidence: ${result.confidence})`);
      } else {
        setError(result.error || 'No speech detected');
        setTranscript('');
      }
      
    } catch (error) {
      console.error('STT processing error:', error);
      setError(`STT failed: ${error.message}`);
      setTranscript('');
    } finally {
      setIsProcessing(false);
      setInterimTranscript('');
      
      if (processingTimeoutRef.current) {
        clearTimeout(processingTimeoutRef.current);
      }
    }
  }, []);

  // Convert audio to WAV format
  const convertToWav = useCallback(async (webmBlob) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = async () => {
        try {
          // Create audio context
          const audioContext = new (window.AudioContext || window.webkitAudioContext)();
          
          // Decode audio data
          const arrayBuffer = reader.result;
          const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
          
          // Convert to WAV
          const wavArrayBuffer = audioBufferToWav(audioBuffer);
          const wavBlob = new Blob([wavArrayBuffer], { type: 'audio/wav' });
          
          resolve(wavBlob);
        } catch (error) {
          console.warn('WAV conversion failed, using original blob:', error);
          resolve(webmBlob); // Fallback to original format
        }
      };
      reader.onerror = () => reject(new Error('Failed to read audio blob'));
      reader.readAsArrayBuffer(webmBlob);
    });
  }, []);

  // Convert AudioBuffer to WAV
  const audioBufferToWav = useCallback((audioBuffer) => {
    const length = audioBuffer.length;
    const sampleRate = audioBuffer.sampleRate;
    const arrayBuffer = new ArrayBuffer(44 + length * 2);
    const view = new DataView(arrayBuffer);
    
    // WAV header
    const writeString = (offset, string) => {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
      }
    };
    
    writeString(0, 'RIFF');
    view.setUint32(4, 36 + length * 2, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    writeString(36, 'data');
    view.setUint32(40, length * 2, true);
    
    // Convert float samples to 16-bit PCM
    const channelData = audioBuffer.getChannelData(0);
    let offset = 44;
    for (let i = 0; i < length; i++) {
      const sample = Math.max(-1, Math.min(1, channelData[i]));
      view.setInt16(offset, sample * 0x7FFF, true);
      offset += 2;
    }
    
    return arrayBuffer;
  }, []);

  // Send audio to STT service
  const sendToSTTService = useCallback(async (audioBlob) => {
    const formData = new FormData();
    formData.append('file', audioBlob, 'audio.wav');
    formData.append('service', 'auto'); // Use auto-selection for best results
    
    const response = await fetch('/api/stt/enhanced', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`STT service error: ${response.status}`);
    }
    
    return await response.json();
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (processingTimeoutRef.current) {
        clearTimeout(processingTimeoutRef.current);
      }
    };
  }, []);

  // Reset transcript
  const resetTranscript = useCallback(() => {
    setTranscript('');
    setInterimTranscript('');
    setError(null);
    setConfidence(0);
    setServiceUsed('');
  }, []);

  // Toggle listening
  const toggleListening = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, startListening, stopListening]);

  return {
    transcript,
    interimTranscript,
    isListening,
    isProcessing,
    error,
    confidence,
    serviceUsed,
    browserSupportsRecording: browserSupportsRecording(),
    startListening,
    stopListening,
    toggleListening,
    resetTranscript
  };
};

export default useEnhancedSpeechRecognition;
