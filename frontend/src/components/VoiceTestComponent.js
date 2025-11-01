import React, { useState, useEffect } from 'react';
import useSpeechRecognition from '../hooks/useSpeechRecognition';
import usePuterTTS from '../hooks/usePuterTTS';
import useVoiceInteraction from '../hooks/useVoiceInteraction';

const VoiceTestComponent = () => {
  const [activeTab, setActiveTab] = useState('recognition');
  const [testText, setTestText] = useState('Hello! This is a test of the text-to-speech functionality.');
  
  // Individual hooks
  const speechRecognition = useSpeechRecognition();
  const tts = usePuterTTS();
  
  // Combined voice interaction hook
  const voiceInteraction = useVoiceInteraction();

  const tabs = [
    { id: 'recognition', label: '🎤 Speech Recognition' },
    { id: 'tts', label: '🔊 Text-to-Speech' },
    { id: 'interaction', label: '💬 Voice Interaction' }
  ];

  return (
    <div style={{ maxWidth: '800px', margin: '20px auto', padding: '20px' }}>
      <h1>🎙️ AI NinjaCoach Voice Hooks Test</h1>
      
      {/* Tab Navigation */}
      <div style={{ marginBottom: '20px' }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '10px 20px',
              margin: '0 5px',
              backgroundColor: activeTab === tab.id ? '#007bff' : '#f8f9fa',
              color: activeTab === tab.id ? 'white' : '#333',
              border: '1px solid #ddd',
              borderRadius: '5px',
              cursor: 'pointer'
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Speech Recognition Tab */}
      {activeTab === 'recognition' && (
        <div>
          <h2>🎤 Speech Recognition Test</h2>
          
          <div style={{ marginBottom: '20px' }}>
            <div style={{ marginBottom: '10px' }}>
              <strong>Support:</strong> {speechRecognition.browserSupportsSpeechRecognition ? '✅ Supported' : '❌ Not Supported'}
            </div>
            <div style={{ marginBottom: '10px' }}>
              <strong>Status:</strong> {speechRecognition.isListening ? '🎙️ Listening...' : '⏸️ Stopped'}
            </div>
            {speechRecognition.error && (
              <div style={{ color: 'red', marginBottom: '10px' }}>
                <strong>Error:</strong> {speechRecognition.error}
              </div>
            )}
          </div>

          <div style={{ marginBottom: '20px' }}>
            <button
              onClick={speechRecognition.startListening}
              disabled={speechRecognition.isListening || !speechRecognition.browserSupportsSpeechRecognition}
              style={{ padding: '10px 20px', margin: '0 10px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '5px' }}
            >
              Start Listening
            </button>
            <button
              onClick={speechRecognition.stopListening}
              disabled={!speechRecognition.isListening}
              style={{ padding: '10px 20px', margin: '0 10px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '5px' }}
            >
              Stop Listening
            </button>
            <button
              onClick={speechRecognition.resetTranscript}
              style={{ padding: '10px 20px', margin: '0 10px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '5px' }}
            >
              Clear
            </button>
          </div>

          <div>
            <h3>Final Transcript:</h3>
            <div style={{ border: '1px solid #ddd', padding: '15px', minHeight: '100px', backgroundColor: '#f8f9fa', borderRadius: '5px' }}>
              {speechRecognition.transcript || 'No speech detected yet...'}
            </div>
          </div>

          {speechRecognition.interimTranscript && (
            <div style={{ marginTop: '10px' }}>
              <h3>Interim Transcript:</h3>
              <div style={{ border: '1px solid #ffc107', padding: '15px', minHeight: '50px', backgroundColor: '#fff3cd', borderRadius: '5px' }}>
                <em>{speechRecognition.interimTranscript}</em>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Text-to-Speech Tab */}
      {activeTab === 'tts' && (
        <div>
          <h2>🔊 Text-to-Speech Test</h2>
          
          <div style={{ marginBottom: '20px' }}>
            <div style={{ marginBottom: '10px' }}>
              <strong>Puter.js Status:</strong> {
                tts.isLoading ? '⏳ Loading...' : 
                tts.isLoaded ? '✅ Loaded' : 
                '❌ Not Loaded'
              }
            </div>
            <div style={{ marginBottom: '10px' }}>
              <strong>TTS Status:</strong> {tts.isSpeaking ? '🔊 Speaking...' : '⏸️ Stopped'}
            </div>
            <div style={{ marginBottom: '10px' }}>
              <strong>Support:</strong> {tts.isSupported ? '✅ Supported' : '❌ Not Supported'}
            </div>
            {tts.error && (
              <div style={{ color: 'red', marginBottom: '10px' }}>
                <strong>Error:</strong> {tts.error}
              </div>
            )}
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '10px' }}>
              <strong>Text to Speak:</strong>
            </label>
            <textarea
              value={testText}
              onChange={(e) => setTestText(e.target.value)}
              style={{ width: '100%', height: '100px', padding: '10px', border: '1px solid #ddd', borderRadius: '5px' }}
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <button
              onClick={() => tts.speak(testText)}
              disabled={tts.isSpeaking || !testText.trim()}
              style={{ padding: '10px 20px', margin: '0 10px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '5px' }}
            >
              Speak
            </button>
            <button
              onClick={tts.stop}
              disabled={!tts.isSpeaking}
              style={{ padding: '10px 20px', margin: '0 10px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '5px' }}
            >
              Stop
            </button>
            <button
              onClick={tts.pause}
              disabled={!tts.isSpeaking}
              style={{ padding: '10px 20px', margin: '0 10px', backgroundColor: '#ffc107', color: 'black', border: 'none', borderRadius: '5px' }}
            >
              Pause
            </button>
            <button
              onClick={tts.resume}
              style={{ padding: '10px 20px', margin: '0 10px', backgroundColor: '#17a2b8', color: 'white', border: 'none', borderRadius: '5px' }}
            >
              Resume
            </button>
          </div>

          <div>
            <h3>Quick Test Phrases:</h3>
            {[
              'Hello, how can I help you today?',
              'This is a test of the emergency broadcast system.',
              'The quick brown fox jumps over the lazy dog.',
              'Welcome to AI NinjaCoach voice interaction!'
            ].map((phrase, index) => (
              <button
                key={index}
                onClick={() => tts.speak(phrase)}
                disabled={tts.isSpeaking}
                style={{ 
                  padding: '8px 12px', 
                  margin: '5px', 
                  backgroundColor: '#6f42c1', 
                  color: 'white', 
                  border: 'none', 
                  borderRadius: '3px',
                  fontSize: '12px'
                }}
              >
                "{phrase.substring(0, 30)}..."
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Voice Interaction Tab */}
      {activeTab === 'interaction' && (
        <div>
          <h2>💬 Voice Interaction Test</h2>
          
          <div style={{ marginBottom: '20px' }}>
            <div style={{ marginBottom: '10px' }}>
              <strong>Status:</strong> {
                voiceInteraction.isActive ? '🟢 Active' : '🔴 Inactive'
              }
            </div>
            <div style={{ marginBottom: '10px' }}>
              <strong>Listening:</strong> {voiceInteraction.isListening ? '🎙️ Yes' : '❌ No'}
            </div>
            <div style={{ marginBottom: '10px' }}>
              <strong>Speaking:</strong> {voiceInteraction.isSpeaking ? '🔊 Yes' : '❌ No'}
            </div>
            <div style={{ marginBottom: '10px' }}>
              <strong>Support:</strong> {voiceInteraction.isSupported ? '✅ Full Support' : '❌ Limited/No Support'}
            </div>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <button
              onClick={voiceInteraction.startVoiceInteraction}
              disabled={voiceInteraction.isActive || !voiceInteraction.isSupported}
              style={{ padding: '15px 25px', margin: '0 10px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '5px', fontSize: '16px' }}
            >
              🚀 Start Voice Interaction
            </button>
            <button
              onClick={voiceInteraction.stopVoiceInteraction}
              disabled={!voiceInteraction.isActive}
              style={{ padding: '15px 25px', margin: '0 10px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '5px', fontSize: '16px' }}
            >
              🛑 Stop Voice Interaction
            </button>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <button
              onClick={() => voiceInteraction.speakAndListen('Hello! I heard you say something. What would you like to talk about?')}
              disabled={!voiceInteraction.isSupported}
              style={{ padding: '10px 15px', margin: '5px', backgroundColor: '#6f42c1', color: 'white', border: 'none', borderRadius: '5px' }}
            >
              Test Speak & Listen
            </button>
            <button
              onClick={() => {
                const text = voiceInteraction.finalizeSpeech();
                if (text) {
                  voiceInteraction.speakAndListen(`You said: ${text}. Thank you for testing!`);
                }
              }}
              disabled={!voiceInteraction.transcript}
              style={{ padding: '10px 15px', margin: '5px', backgroundColor: '#fd7e14', color: 'white', border: 'none', borderRadius: '5px' }}
            >
              Finalize & Respond
            </button>
            <button
              onClick={voiceInteraction.clearHistory}
              style={{ padding: '10px 15px', margin: '5px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '5px' }}
            >
              Clear History
            </button>
          </div>

          <div>
            <h3>Current Transcript:</h3>
            <div style={{ border: '1px solid #ddd', padding: '15px', minHeight: '80px', backgroundColor: '#f8f9fa', borderRadius: '5px' }}>
              <strong>Final:</strong> {voiceInteraction.transcript || 'None'}
              <br />
              <strong>Interim:</strong> <em>{voiceInteraction.interimTranscript || 'None'}</em>
            </div>
          </div>

          <div style={{ marginTop: '20px' }}>
            <h3>Conversation History ({voiceInteraction.conversationHistory.length} messages):</h3>
            <div style={{ border: '1px solid #ddd', padding: '15px', maxHeight: '200px', overflowY: 'auto', backgroundColor: '#fff', borderRadius: '5px' }}>
              {voiceInteraction.conversationHistory.length === 0 ? (
                <p style={{ color: '#6c757d', fontStyle: 'italic' }}>No conversation history yet...</p>
              ) : (
                voiceInteraction.conversationHistory.map((entry) => (
                  <div key={entry.id} style={{ marginBottom: '10px', padding: '8px', backgroundColor: entry.type === 'user' ? '#e3f2fd' : '#f3e5f5', borderRadius: '3px' }}>
                    <strong>{entry.type === 'user' ? '👤 User' : '🤖 Assistant'}:</strong> {entry.message}
                    <br />
                    <small style={{ color: '#6c757d' }}>{new Date(entry.timestamp).toLocaleTimeString()}</small>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceTestComponent;
