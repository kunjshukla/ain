import React, { useState } from 'react';
import { usePuterTTS } from '../hooks/usePuterTTS';
import useSimplePuterTTS from '../hooks/useSimplePuterTTS';

const PuterTTSComparison = () => {
  const [activeVersion, setActiveVersion] = useState('full');
  
  // Full-featured hook
  const fullTTS = usePuterTTS();
  
  // Simple hook
  const simpleTTS = useSimplePuterTTS();

  const testText = "Hello! This is a test of Puter.js text-to-speech functionality in AI NinjaCoach.";

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>🎤 Puter.js TTS Hook Comparison</h1>
      
      {/* Version Selector */}
      <div style={{ marginBottom: '30px' }}>
        <button 
          onClick={() => setActiveVersion('full')}
          style={{
            padding: '10px 20px',
            margin: '5px',
            backgroundColor: activeVersion === 'full' ? '#007bff' : '#f8f9fa',
            color: activeVersion === 'full' ? 'white' : '#333',
            border: '1px solid #ddd',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          📦 Full Featured Hook
        </button>
        <button 
          onClick={() => setActiveVersion('simple')}
          style={{
            padding: '10px 20px',
            margin: '5px',
            backgroundColor: activeVersion === 'simple' ? '#007bff' : '#f8f9fa',
            color: activeVersion === 'simple' ? 'white' : '#333',
            border: '1px solid #ddd',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          ⚡ Simple Hook
        </button>
      </div>

      {/* Full Featured Version */}
      {activeVersion === 'full' && (
        <div>
          <h2>📦 Full Featured usePuterTTS Hook</h2>
          
          <div style={{ 
            padding: '15px', 
            backgroundColor: '#f8f9fa', 
            borderRadius: '8px', 
            marginBottom: '20px' 
          }}>
            <h3>Status</h3>
            <p>✅ <strong>Loaded:</strong> {fullTTS.isLoaded ? 'Yes' : 'No'}</p>
            <p>⏳ <strong>Loading:</strong> {fullTTS.isLoading ? 'Yes' : 'No'}</p>
            <p>🔊 <strong>Speaking:</strong> {fullTTS.isSpeaking ? 'Yes' : 'No'}</p>
            <p>🎯 <strong>Supported:</strong> {fullTTS.isSupported ? 'Yes' : 'No'}</p>
            {fullTTS.error && <p style={{color: 'red'}}>❌ <strong>Error:</strong> {fullTTS.error}</p>}
          </div>

          <div style={{ marginBottom: '20px' }}>
            <button 
              onClick={() => fullTTS.speak(testText)}
              disabled={fullTTS.isSpeaking}
              style={{
                padding: '12px 20px',
                margin: '5px',
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer'
              }}
            >
              🗣️ Speak Test Text
            </button>
            
            <button 
              onClick={() => fullTTS.speak("This is a custom voice test", {
                voice: 'en-US-Neural2-B',
                rate: 1.3,
                pitch: 1.2
              })}
              disabled={fullTTS.isSpeaking}
              style={{
                padding: '12px 20px',
                margin: '5px',
                backgroundColor: '#6f42c1',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer'
              }}
            >
              🎛️ Custom Voice
            </button>
            
            <button 
              onClick={fullTTS.stop}
              disabled={!fullTTS.isSpeaking}
              style={{
                padding: '12px 20px',
                margin: '5px',
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer'
              }}
            >
              🛑 Stop
            </button>
          </div>

          <div style={{ 
            padding: '15px', 
            backgroundColor: '#e8f5e8', 
            borderRadius: '8px' 
          }}>
            <h4>✅ Features:</h4>
            <ul>
              <li>Complete loading state management</li>
              <li>Voice customization (rate, pitch, volume)</li>
              <li>Pause/resume functionality</li>
              <li>Error handling and fallbacks</li>
              <li>Audio format options</li>
              <li>Comprehensive status reporting</li>
            </ul>
          </div>
        </div>
      )}

      {/* Simple Version */}
      {activeVersion === 'simple' && (
        <div>
          <h2>⚡ Simple usePuterTTS Hook</h2>
          
          <div style={{ 
            padding: '15px', 
            backgroundColor: '#f8f9fa', 
            borderRadius: '8px', 
            marginBottom: '20px' 
          }}>
            <h3>Status</h3>
            <p>✅ <strong>Ready:</strong> {simpleTTS.isReady ? 'Yes' : 'No'}</p>
            <p>🔊 <strong>Speaking:</strong> {simpleTTS.isSpeaking ? 'Yes' : 'No'}</p>
            {simpleTTS.error && <p style={{color: 'red'}}>❌ <strong>Error:</strong> {simpleTTS.error}</p>}
          </div>

          <div style={{ marginBottom: '20px' }}>
            <button 
              onClick={() => simpleTTS.speak(testText)}
              disabled={simpleTTS.isSpeaking || !simpleTTS.isReady}
              style={{
                padding: '12px 20px',
                margin: '5px',
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer'
              }}
            >
              🗣️ Simple Speak
            </button>
            
            <button 
              onClick={simpleTTS.stop}
              disabled={!simpleTTS.isSpeaking}
              style={{
                padding: '12px 20px',
                margin: '5px',
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer'
              }}
            >
              🛑 Stop
            </button>
          </div>

          <div style={{ 
            padding: '15px', 
            backgroundColor: '#fff3cd', 
            borderRadius: '8px' 
          }}>
            <h4>⚡ Features:</h4>
            <ul>
              <li>Minimal API surface</li>
              <li>Easy to understand and use</li>
              <li>Automatic fallback to Web Speech API</li>
              <li>Basic error handling</li>
              <li>Lightweight implementation</li>
            </ul>
          </div>
        </div>
      )}

      {/* Code Examples */}
      <div style={{ marginTop: '40px' }}>
        <h2>💻 Code Examples</h2>
        
        <div style={{ marginBottom: '20px' }}>
          <h3>Full Featured Hook Usage:</h3>
          <pre style={{ 
            backgroundColor: '#f8f9fa', 
            padding: '15px', 
            borderRadius: '5px',
            fontSize: '14px',
            overflow: 'auto'
          }}>
{`import { usePuterTTS } from './hooks/usePuterTTS';

function MyComponent() {
  const { speak, isLoaded, isSpeaking, stop } = usePuterTTS();
  
  const handleSpeak = () => {
    speak("Hello world!", {
      voice: 'en-US-Neural2-A',
      rate: 1.2,
      pitch: 1.1,
      volume: 0.8
    });
  };
  
  return (
    <div>
      <button onClick={handleSpeak} disabled={!isLoaded || isSpeaking}>
        Speak
      </button>
      <button onClick={stop} disabled={!isSpeaking}>
        Stop
      </button>
    </div>
  );
}`}
          </pre>
        </div>

        <div>
          <h3>Simple Hook Usage:</h3>
          <pre style={{ 
            backgroundColor: '#f8f9fa', 
            padding: '15px', 
            borderRadius: '5px',
            fontSize: '14px',
            overflow: 'auto'
          }}>
{`import useSimplePuterTTS from './hooks/useSimplePuterTTS';

function MyComponent() {
  const { speak, isReady, isSpeaking, stop } = useSimplePuterTTS();
  
  return (
    <div>
      <button onClick={() => speak("Hello world!")} disabled={!isReady}>
        Speak
      </button>
      <button onClick={stop} disabled={!isSpeaking}>
        Stop
      </button>
    </div>
  );
}`}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default PuterTTSComparison;
