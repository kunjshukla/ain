import React, { useState, useEffect, useRef } from 'react';
import useSpeechRecognition from '../hooks/useSpeechRecognition';
import usePuterTTS from '../hooks/usePuterTTS';
import { socket, startInterview, submitAnswer, requestNextQuestion, endInterview } from '../services/socket';

const VoiceInterview = () => {
  // State management
  const [isVoiceModeActive, setIsVoiceModeActive] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [questionId, setQuestionId] = useState(null);
  const [interviewStatus, setInterviewStatus] = useState('idle'); // idle, active, ended
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const [conversationHistory, setConversationHistory] = useState([]);

  // Hooks
  const speechRecognition = useSpeechRecognition();
  const tts = usePuterTTS();

  // Refs
  const transcriptRef = useRef(null);
  const conversationRef = useRef(null);

  // Socket connection management
  useEffect(() => {
    const handleConnect = () => {
      console.log('Connected to server');
      setIsConnected(true);
      setError(null);
    };

    const handleDisconnect = () => {
      console.log('Disconnected from server');
      setIsConnected(false);
    };

    const handleConnectError = (error) => {
      console.error('Connection error:', error);
      setError('Failed to connect to server');
      setIsConnected(false);
    };

    // Set up socket event listeners
    socket.on('connect', handleConnect);
    socket.on('disconnect', handleDisconnect);
    socket.on('connect_error', handleConnectError);

    // Check initial connection status
    setIsConnected(socket.connected);

    // Cleanup on unmount
    return () => {
      socket.off('connect', handleConnect);
      socket.off('disconnect', handleDisconnect);
      socket.off('connect_error', handleConnectError);
    };
  }, []);

  // Voice recognition management
  useEffect(() => {
    if (isVoiceModeActive && speechRecognition.isSupported) {
      speechRecognition.startListening();
    } else {
      speechRecognition.stopListening();
    }
  }, [isVoiceModeActive, speechRecognition]);

  // Update transcript when speech recognition changes
  useEffect(() => {
    if (speechRecognition.transcript) {
      setTranscript(speechRecognition.transcript);
    }
  }, [speechRecognition.transcript]);

  // Auto-scroll transcript
  useEffect(() => {
    if (transcriptRef.current) {
      transcriptRef.current.scrollTop = transcriptRef.current.scrollHeight;
    }
  }, [transcript]);

  // Auto-scroll conversation history
  useEffect(() => {
    if (conversationRef.current) {
      conversationRef.current.scrollTop = conversationRef.current.scrollHeight;
    }
  }, [conversationHistory]);

  // Voice mode toggle
  const toggleVoiceMode = () => {
    if (!speechRecognition.isSupported) {
      setError('Speech recognition is not supported in this browser');
      return;
    }

    if (!isConnected) {
      setError('Please connect to server first');
      return;
    }

    setIsVoiceModeActive(!isVoiceModeActive);
    setError(null);
  };

  // Start interview
  const handleStartInterview = async () => {
    if (!isConnected) {
      setError('Not connected to server');
      return;
    }

    try {
      setError(null);
      const response = await startInterview({
        userId: 'voice_user_' + Date.now(),
        interviewType: 'technical'
      });

      if (response.error) {
        throw new Error(response.error);
      }

      setSessionId(response.session_id);
      setQuestionId(response.current_question_id);
      setCurrentQuestion(response.current_question);
      setInterviewStatus('active');

      // Add first question to conversation history
      setConversationHistory([{
        type: 'question',
        content: response.current_question,
        timestamp: new Date().toLocaleTimeString()
      }]);

      // Speak the first question if TTS is available
      if (tts.isSupported && response.current_question) {
        await tts.speak(response.current_question);
      }

    } catch (error) {
      setError(`Failed to start interview: ${error.message}`);
      console.error('Start interview error:', error);
    }
  };

  // Submit answer
  const handleSubmitAnswer = async () => {
    if (!transcript.trim()) {
      setError('Please provide an answer');
      return;
    }

    if (!sessionId || !questionId) {
      setError('No active interview session');
      return;
    }

    try {
      setError(null);

      // Add answer to conversation history
      setConversationHistory(prev => [...prev, {
        type: 'answer',
        content: transcript,
        timestamp: new Date().toLocaleTimeString()
      }]);

      // Submit answer to backend
      const response = await submitAnswer(transcript, questionId);

      if (response.error) {
        throw new Error(response.error);
      }

      // Add feedback to conversation history if available
      if (response.feedback) {
        setConversationHistory(prev => [...prev, {
          type: 'feedback',
          content: response.feedback,
          timestamp: new Date().toLocaleTimeString()
        }]);

        // Speak feedback if TTS is available
        if (tts.isSupported) {
          await tts.speak(response.feedback);
        }
      }

      // Clear transcript
      setTranscript('');
      speechRecognition.resetTranscript();

      // Auto-request next question after a brief pause
      setTimeout(() => {
        handleNextQuestion();
      }, 2000);

    } catch (error) {
      setError(`Failed to submit answer: ${error.message}`);
      console.error('Submit answer error:', error);
    }
  };

  // Get next question
  const handleNextQuestion = async () => {
    if (!sessionId) {
      setError('No active interview session');
      return;
    }

    try {
      setError(null);
      const response = await requestNextQuestion();

      if (response.error) {
        throw new Error(response.error);
      }

      setQuestionId(response.question_id);
      setCurrentQuestion(response.question);

      // Add new question to conversation history
      setConversationHistory(prev => [...prev, {
        type: 'question',
        content: response.question,
        timestamp: new Date().toLocaleTimeString()
      }]);

      // Speak the new question if TTS is available
      if (tts.isSupported && response.question) {
        await tts.speak(response.question);
      }

    } catch (error) {
      setError(`Failed to get next question: ${error.message}`);
      console.error('Next question error:', error);
    }
  };

  // End interview
  const handleEndInterview = async () => {
    if (!sessionId) {
      setError('No active interview session');
      return;
    }

    try {
      setError(null);
      const response = await endInterview();

      if (response.error) {
        throw new Error(response.error);
      }

      setInterviewStatus('ended');
      setSessionId(null);
      setQuestionId(null);
      setCurrentQuestion('');

      // Add final feedback to conversation history
      if (response.final_feedback) {
        setConversationHistory(prev => [...prev, {
          type: 'final_feedback',
          content: response.final_feedback,
          timestamp: new Date().toLocaleTimeString()
        }]);

        // Speak final feedback if TTS is available
        if (tts.isSupported) {
          await tts.speak(response.final_feedback);
        }
      }

      // Stop voice mode
      setIsVoiceModeActive(false);

    } catch (error) {
      setError(`Failed to end interview: ${error.message}`);
      console.error('End interview error:', error);
    }
  };

  // Clear conversation
  const clearConversation = () => {
    setConversationHistory([]);
    setTranscript('');
    speechRecognition.resetTranscript();
    setError(null);
  };

  return (
    <div style={{ maxWidth: '800px', margin: '20px auto', padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: '30px' }}>
        <h1>🎙️ AI NinjaCoach Voice Interview</h1>
        <div style={{
          padding: '10px',
          borderRadius: '8px',
          backgroundColor: isConnected ? '#d4edda' : '#f8d7da',
          color: isConnected ? '#155724' : '#721c24',
          border: `1px solid ${isConnected ? '#c3e6cb' : '#f5c6cb'}`,
          marginBottom: '20px'
        }}>
          {isConnected ? '✅ Connected to server' : '❌ Disconnected from server'}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div style={{
          padding: '15px',
          backgroundColor: '#f8d7da',
          color: '#721c24',
          border: '1px solid #f5c6cb',
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          ⚠️ {error}
        </div>
      )}

      {/* Interview Controls */}
      <div style={{ 
        display: 'flex', 
        gap: '10px', 
        marginBottom: '20px',
        flexWrap: 'wrap',
        justifyContent: 'center'
      }}>
        {interviewStatus === 'idle' && (
          <button
            onClick={handleStartInterview}
            disabled={!isConnected}
            style={{
              padding: '12px 24px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: isConnected ? 'pointer' : 'not-allowed',
              fontSize: '16px',
              opacity: isConnected ? 1 : 0.6
            }}
          >
            🚀 Start Interview
          </button>
        )}

        {interviewStatus === 'active' && (
          <>
            <button
              onClick={toggleVoiceMode}
              style={{
                padding: '12px 24px',
                backgroundColor: isVoiceModeActive ? '#dc3545' : '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '16px'
              }}
            >
              {isVoiceModeActive ? '🎤 Stop Voice' : '🎤 Start Voice'}
            </button>

            <button
              onClick={handleSubmitAnswer}
              disabled={!transcript.trim()}
              style={{
                padding: '12px 24px',
                backgroundColor: '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: transcript.trim() ? 'pointer' : 'not-allowed',
                fontSize: '16px',
                opacity: transcript.trim() ? 1 : 0.6
              }}
            >
              📤 Send Answer
            </button>

            <button
              onClick={handleNextQuestion}
              style={{
                padding: '12px 24px',
                backgroundColor: '#ffc107',
                color: '#212529',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '16px'
              }}
            >
              ⏭️ Next Question
            </button>

            <button
              onClick={handleEndInterview}
              style={{
                padding: '12px 24px',
                backgroundColor: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '16px'
              }}
            >
              🏁 End Interview
            </button>
          </>
        )}

        <button
          onClick={clearConversation}
          style={{
            padding: '12px 24px',
            backgroundColor: '#e9ecef',
            color: '#495057',
            border: '1px solid #ced4da',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          🗑️ Clear
        </button>
      </div>

      {/* Voice Status */}
      {isVoiceModeActive && (
        <div style={{
          padding: '15px',
          backgroundColor: speechRecognition.isListening ? '#d1ecf1' : '#f8d7da',
          color: speechRecognition.isListening ? '#0c5460' : '#721c24',
          border: `1px solid ${speechRecognition.isListening ? '#bee5eb' : '#f5c6cb'}`,
          borderRadius: '8px',
          marginBottom: '20px',
          textAlign: 'center'
        }}>
          {speechRecognition.isListening ? '🎤 Listening... Speak now!' : '⏸️ Voice recognition paused'}
        </div>
      )}

      {/* Current Question */}
      {currentQuestion && (
        <div style={{
          padding: '20px',
          backgroundColor: '#e3f2fd',
          border: '1px solid #bbdefb',
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          <h3 style={{ margin: '0 0 10px 0', color: '#1976d2' }}>❓ Current Question:</h3>
          <p style={{ margin: 0, fontSize: '16px', lineHeight: '1.5' }}>{currentQuestion}</p>
        </div>
      )}

      {/* Transcript Display */}
      <div style={{ marginBottom: '20px' }}>
        <h3 style={{ marginBottom: '10px', color: '#333' }}>🎯 Your Response:</h3>
        <div
          ref={transcriptRef}
          style={{
            minHeight: '120px',
            maxHeight: '200px',
            padding: '15px',
            border: '2px solid #e9ecef',
            borderRadius: '8px',
            backgroundColor: '#f8f9fa',
            overflowY: 'auto',
            fontSize: '16px',
            lineHeight: '1.5',
            whiteSpace: 'pre-wrap'
          }}
        >
          {transcript || 'Your speech will appear here...'}
        </div>
        {speechRecognition.confidence && (
          <small style={{ color: '#6c757d', marginTop: '5px', display: 'block' }}>
            Confidence: {Math.round(speechRecognition.confidence * 100)}%
          </small>
        )}
      </div>

      {/* Conversation History */}
      {conversationHistory.length > 0 && (
        <div>
          <h3 style={{ marginBottom: '10px', color: '#333' }}>💬 Conversation History:</h3>
          <div
            ref={conversationRef}
            style={{
              maxHeight: '400px',
              border: '1px solid #e9ecef',
              borderRadius: '8px',
              backgroundColor: '#ffffff',
              overflowY: 'auto',
              padding: '0'
            }}
          >
            {conversationHistory.map((item, index) => (
              <div
                key={index}
                style={{
                  padding: '15px',
                  borderBottom: index < conversationHistory.length - 1 ? '1px solid #e9ecef' : 'none',
                  backgroundColor: item.type === 'question' ? '#e3f2fd' : 
                                  item.type === 'answer' ? '#f3e5f5' : 
                                  item.type === 'feedback' ? '#e8f5e8' : '#fff3cd'
                }}
              >
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  marginBottom: '8px'
                }}>
                  <strong style={{ 
                    color: item.type === 'question' ? '#1976d2' : 
                           item.type === 'answer' ? '#7b1fa2' : 
                           item.type === 'feedback' ? '#388e3c' : '#f57c00'
                  }}>
                    {item.type === 'question' ? '❓ Interviewer' : 
                     item.type === 'answer' ? '🎯 You' : 
                     item.type === 'feedback' ? '💡 Feedback' : '🏆 Final Feedback'}
                  </strong>
                  <small style={{ color: '#6c757d' }}>{item.timestamp}</small>
                </div>
                <p style={{ margin: 0, lineHeight: '1.5' }}>{item.content}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TTS Status */}
      {tts.isSpeaking && (
        <div style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          padding: '10px 15px',
          backgroundColor: '#007bff',
          color: 'white',
          borderRadius: '25px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
          fontSize: '14px'
        }}>
          🔊 Speaking...
        </div>
      )}
    </div>
  );
};

export default VoiceInterview;
