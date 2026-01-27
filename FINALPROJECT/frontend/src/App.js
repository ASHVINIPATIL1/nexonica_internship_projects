/**
 * Main App Component
 * AI-Enhanced Hand Tracking Whiteboard
 */

import React, { useState, useEffect } from 'react';
import './App.css';
import VideoCanvas from './components/VideoCanvas';
import Toolbar from './components/Toolbar';
import StatusBar from './components/StatusBar';
import websocketService from './services/websocket';
import * as api from './services/api';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [videoStarted, setVideoStarted] = useState(false);
  const [status, setStatus] = useState({
    mode: 'IDLE',
    color: 'red',
    brush_size: 5,
    can_undo: false,
    can_redo: false,
    hand_detected: false
  });

  useEffect(() => {
    websocketService.connect();
    
    websocketService.socket.on('connect', () => {
      console.log('✅ Connected to backend');
      setIsConnected(true);
    });

    websocketService.socket.on('disconnect', () => {
      console.log('❌ Disconnected from backend');
      setIsConnected(false);
      setVideoStarted(false);
    });

    return () => {
      websocketService.disconnect();
    };
  }, []);

  useEffect(() => {
    if (!isConnected) return;

    const statusInterval = setInterval(async () => {
      try {
        const statusData = await api.getStatus();
        setStatus(statusData);
      } catch (error) {
        console.error('Error fetching status:', error);
      }
    }, 500);

    return () => clearInterval(statusInterval);
  }, [isConnected]);

  const handleStartVideo = () => {
    websocketService.startVideo();
    setVideoStarted(true);
  };

  const handleClearCanvas = async () => {
    try {
      await api.clearCanvas();
    } catch (error) {
      console.error('Error clearing canvas:', error);
    }
  };

  const handleUndo = async () => {
    try {
      await api.undo();
    } catch (error) {
      console.error('Error undoing:', error);
    }
  };

  const handleRedo = async () => {
    try {
      await api.redo();
    } catch (error) {
      console.error('Error redoing:', error);
    }
  };

  const handlePerfectShape = async () => {
    try {
      const result = await api.perfectShape();
      console.log('✨', result.message);
    } catch (error) {
      console.error('Error applying shape recognition:', error);
    }
  };

  const handleChangeColor = async (color) => {
    try {
      await api.changeColor(color);
    } catch (error) {
      console.error('Error changing color:', error);
    }
  };

  const handleChangeBrushSize = async (size) => {
    try {
      await api.changeBrushSize(size);
    } catch (error) {
      console.error('Error changing brush size:', error);
    }
  };

  const handleSaveCanvas = async () => {
    try {
      const result = await api.saveCanvas();
      alert(`Canvas saved as: ${result.filename}`);
    } catch (error) {
      console.error('Error saving canvas:', error);
      alert('Error saving canvas');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎨 AI Whiteboard</h1>
        <div className="connection-status">
          {isConnected ? (
            <span className="status-connected">● Connected</span>
          ) : (
            <span className="status-disconnected">● Disconnected</span>
          )}
        </div>
      </header>

      <main className="App-main">
        {!isConnected ? (
          <div className="connection-message">
            <h2>Connecting to backend...</h2>
            <p>Make sure the Python backend is running on port 5000</p>
            <code>python app.py</code>
          </div>
        ) : !videoStarted ? (
          <div className="start-message">
            <h2>Ready to Start!</h2>
            <p>Click the button below to start your AI whiteboard</p>
            <button className="btn-start" onClick={handleStartVideo}>
              🚀 Start Whiteboard
            </button>
          </div>
        ) : (
          <>
            <Toolbar
              onClearCanvas={handleClearCanvas}
              onUndo={handleUndo}
              onRedo={handleRedo}
              onPerfectShape={handlePerfectShape}
              onChangeColor={handleChangeColor}
              onChangeBrushSize={handleChangeBrushSize}
              onSaveCanvas={handleSaveCanvas}
              currentColor={status.color}
              brushSize={status.brush_size}
              canUndo={status.can_undo}
              canRedo={status.can_redo}
            />
            
            <VideoCanvas />
            
            <StatusBar
              mode={status.mode}
              color={status.color}
              brushSize={status.brush_size}
              handDetected={status.hand_detected}
              canUndo={status.can_undo}
              canRedo={status.can_redo}
            />
          </>
        )}
      </main>

      <footer className="App-footer">
        <p>Hand Tracking Whiteboard | Use gestures to draw and create!</p>
      </footer>
    </div>
  );
}

export default App;
