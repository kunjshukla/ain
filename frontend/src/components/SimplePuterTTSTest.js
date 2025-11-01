import React from 'react';
import { usePuterTTS } from '../hooks/usePuterTTS';

const SimplePuterTTSTest = () => {
  const { speak, isLoaded, isLoading, isSpeaking, error, stop } = usePuterTTS();

  const testSpeak = () => {
    speak("Hello! This is a test of Puter.js text-to-speech functionality.");
  };

  const testCustomVoice = () => {
    speak("This is a custom voice test with different settings.", {
      voice: 'en-US-Neural2-A',
      rate: 1.2,
      pitch: 1.1,
      volume: 0.8
    });
  };

  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
      <h2>🎤 Puter.js TTS Hook Test</h2>
      
      {/* Status Display */}
      <div style={{ 
        padding: '15px', 
        border: '1px solid #ddd', 
        borderRadius: '8px', 
        marginBottom: '20px',
        backgroundColor: '#f8f9fa'
      }}>
        <h3>Status</h3>
        <p><strong>Loading:</strong> {isLoading ? '⏳ Loading Puter.js...' : '✅ Ready'}</p>
        <p><strong>Loaded:</strong> {isLoaded ? '✅ Puter.js Loaded' : '❌ Not Loaded'}</p>
        <p><strong>Speaking:</strong> {isSpeaking ? '🔊 Speaking...' : '⏸️ Silent'}</p>
        {error && (
          <p style={{ color: 'red' }}><strong>Error:</strong> {error}</p>
        )}
      </div>

      {/* Controls */}
      <div style={{ marginBottom: '20px' }}>
        <button 
          onClick={testSpeak}
          disabled={isSpeaking || isLoading}
          style={{
            padding: '12px 20px',
            margin: '5px',
            backgroundColor: isSpeaking ? '#6c757d' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: isSpeaking ? 'not-allowed' : 'pointer'
          }}
        >
          🗣️ Test Basic Speech
        </button>

        <button 
          onClick={testCustomVoice}
          disabled={isSpeaking || isLoading}
          style={{
            padding: '12px 20px',
            margin: '5px',
            backgroundColor: isSpeaking ? '#6c757d' : '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: isSpeaking ? 'not-allowed' : 'pointer'
          }}
        >
          🎛️ Test Custom Voice
        </button>

        <button 
          onClick={stop}
          disabled={!isSpeaking}
          style={{
            padding: '12px 20px',
            margin: '5px',
            backgroundColor: !isSpeaking ? '#6c757d' : '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: !isSpeaking ? 'not-allowed' : 'pointer'
          }}
        >
          🛑 Stop
        </button>
      </div>

      {/* Quick Test Phrases */}
      <div>
        <h3>Quick Test Phrases</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {[
            'Hello, world!',
            'How are you today?',
            'This is AI NinjaCoach speaking.',
            'The quick brown fox jumps over the lazy dog.',
            'Welcome to our interview coaching platform!'
          ].map((phrase, index) => (
            <button
              key={index}
              onClick={() => speak(phrase)}
              disabled={isSpeaking || isLoading}
              style={{
                padding: '8px 12px',
                fontSize: '12px',
                backgroundColor: '#6f42c1',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: isSpeaking ? 'not-allowed' : 'pointer',
                opacity: isSpeaking ? 0.6 : 1
              }}
            >
              "{phrase.substring(0, 20)}..."
            </button>
          ))}
        </div>
      </div>

      {/* Instructions */}
      <div style={{ 
        marginTop: '30px', 
        padding: '15px', 
        backgroundColor: '#e3f2fd', 
        borderRadius: '8px' 
      }}>
        <h3>📋 Instructions</h3>
        <ol>
          <li>Wait for Puter.js to load (should be automatic)</li>
          <li>Click any speech button to test TTS functionality</li>
          <li>If Puter.js fails, it will fallback to Web Speech API</li>
          <li>Use the Stop button to interrupt speech</li>
          <li>Try different phrases to test voice quality</li>
        </ol>
      </div>
    </div>
  );
};

export default SimplePuterTTSTest;
