import { io } from 'socket.io-client';

// Socket.io client configuration
const SOCKET_URL = 'http://localhost:8000';

// Create socket connection
const socket = io(SOCKET_URL, {
  // Connection options
  autoConnect: true,
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionAttempts: 5,
  timeout: 20000,
  transports: ['websocket', 'polling'],
  
  // Additional options for FastAPI compatibility
  path: '/socket.io/',
  
  // CORS and headers
  withCredentials: false,
  extraHeaders: {
    'Content-Type': 'application/json'
  }
});

// Connection event handlers
socket.on('connect', () => {
  console.log('✅ Connected to server:', socket.id);
});

socket.on('disconnect', (reason) => {
  console.log('❌ Disconnected from server:', reason);
});

socket.on('connect_error', (error) => {
  console.error('🔴 Connection error:', error);
});

socket.on('reconnect', (attemptNumber) => {
  console.log('🔄 Reconnected to server after', attemptNumber, 'attempts');
});

socket.on('reconnect_failed', () => {
  console.error('💥 Failed to reconnect to server');
});

// Helper function to send messages with error handling
const sendMessage = (event, data, callback) => {
  return new Promise((resolve, reject) => {
    try {
      if (!socket.connected) {
        throw new Error('Socket is not connected');
      }

      // Send message with acknowledgment
      socket.emit(event, data, (response) => {
        if (response && response.error) {
          reject(new Error(response.error));
        } else {
          resolve(response);
        }
        
        // Call optional callback
        if (callback && typeof callback === 'function') {
          callback(response);
        }
      });
      
    } catch (error) {
      reject(error);
    }
  });
};

// Helper function to listen to events with cleanup
const listenToEvent = (event, handler) => {
  socket.on(event, handler);
  
  // Return cleanup function
  return () => {
    socket.off(event, handler);
  };
};

// Helper function to send and wait for response
const sendAndWait = async (event, data, timeout = 5000) => {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error(`Timeout waiting for response to ${event}`));
    }, timeout);

    socket.emit(event, data, (response) => {
      clearTimeout(timer);
      if (response && response.error) {
        reject(new Error(response.error));
      } else {
        resolve(response);
      }
    });
  });
};

// Helper function to check connection status
const isConnected = () => {
  return socket.connected;
};

// Helper function to get connection ID
const getSocketId = () => {
  return socket.id;
};

// Helper function to manually connect/disconnect
const connect = () => {
  if (!socket.connected) {
    socket.connect();
  }
};

const disconnect = () => {
  if (socket.connected) {
    socket.disconnect();
  }
};

// Interview-specific helper functions
const startInterview = async (sessionData) => {
  return sendAndWait('start_interview', sessionData);
};

const submitAnswer = async (answer, questionId) => {
  return sendAndWait('submit_answer', { answer, questionId });
};

const requestNextQuestion = async () => {
  return sendAndWait('next_question', {});
};

const endInterview = async () => {
  return sendAndWait('end_interview', {});
};

// Resume processing helper functions
const submitResume = async (resumeData) => {
  return sendAndWait('submit_resume', resumeData);
};

const getResumeAnalysis = async (jobId) => {
  return sendAndWait('get_resume_analysis', { job_id: jobId });
};

// Voice interaction helper functions
const sendVoiceData = async (audioData) => {
  return sendAndWait('voice_input', { audio: audioData });
};

const requestTTS = async (text, options = {}) => {
  return sendAndWait('tts_request', { text, options });
};

// Export socket instance and helper functions
export {
  socket,
  sendMessage,
  listenToEvent,
  sendAndWait,
  isConnected,
  getSocketId,
  connect,
  disconnect,
  
  // Interview helpers
  startInterview,
  submitAnswer,
  requestNextQuestion,
  endInterview,
  
  // Resume processing helpers
  submitResume,
  getResumeAnalysis,
  
  // Voice interaction helpers
  sendVoiceData,
  requestTTS
};

// Default export
export default socket;
