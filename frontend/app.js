import React, { useState } from 'react';
import VoiceInterview from './src/components/VoiceInterview';
import VoiceTestComponent from './src/components/VoiceTestComponent';

function App() {
  const [activeView, setActiveView] = useState('interview');

  const views = [
    { id: 'interview', label: '🎙️ Voice Interview', component: VoiceInterview },
    { id: 'test', label: '🧪 Voice Test', component: VoiceTestComponent }
  ];

  const ActiveComponent = views.find(view => view.id === activeView)?.component || VoiceInterview;

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      {/* Navigation */}
      <nav style={{
        backgroundColor: '#343a40',
        padding: '15px 0',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          display: 'flex',
          justifyContent: 'center',
          gap: '20px',
          padding: '0 20px'
        }}>
          {views.map(view => (
            <button
              key={view.id}
              onClick={() => setActiveView(view.id)}
              style={{
                padding: '12px 24px',
                backgroundColor: activeView === view.id ? '#007bff' : 'transparent',
                color: activeView === view.id ? 'white' : '#ffffff',
                border: `2px solid ${activeView === view.id ? '#007bff' : '#6c757d'}`,
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: '500',
                transition: 'all 0.3s ease'
              }}
            >
              {view.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Header */}
      <header style={{
        backgroundColor: 'white',
        padding: '30px 0',
        textAlign: 'center',
        borderBottom: '1px solid #e9ecef'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 20px'
        }}>
          <h1 style={{
            margin: '0 0 10px 0',
            color: '#343a40',
            fontSize: '2.5rem',
            fontWeight: '300'
          }}>
            🥷 AI NinjaCoach
          </h1>
          <p style={{
            margin: 0,
            color: '#6c757d',
            fontSize: '1.2rem'
          }}>
            Voice-Powered Interview Practice Platform
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '0 20px'
      }}>
        <ActiveComponent />
      </main>

      {/* Footer */}
      <footer style={{
        backgroundColor: '#343a40',
        color: 'white',
        textAlign: 'center',
        padding: '30px 0',
        marginTop: '50px'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 20px'
        }}>
          <p style={{ margin: '0 0 10px 0' }}>
            🚀 AI NinjaCoach - Open Source Voice Interview Platform
          </p>
          <p style={{ margin: 0, color: '#adb5bd', fontSize: '14px' }}>
            Powered by FastAPI, Socket.io, React, and Ollama
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
