/**
 * WebSocket Service
 * Handles real-time video streaming
 */

import { io } from 'socket.io-client';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
  }

  connect() {
    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';
    
    this.socket = io(backendUrl, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5
    });

    this.socket.on('connect', () => {
      console.log('✅ WebSocket connected');
      this.isConnected = true;
    });

    this.socket.on('disconnect', () => {
      console.log('❌ WebSocket disconnected');
      this.isConnected = false;
    });

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }

  startVideo() {
    if (this.socket && this.isConnected) {
      this.socket.emit('start_video');
      console.log('📹 Video stream started');
    }
  }

  stopVideo() {
    if (this.socket && this.isConnected) {
      this.socket.emit('stop_video');
      console.log('🛑 Video stream stopped');
    }
  }

  onVideoFrame(callback) {
    if (this.socket) {
      this.socket.on('video_frame', callback);
    }
  }
}

const websocketService = new WebSocketService();
export default websocketService;
