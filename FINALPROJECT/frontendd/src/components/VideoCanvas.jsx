/**
 * VideoCanvas Component
 * Displays video stream with drawings
 */

import React, { useEffect, useRef, useState } from 'react';
import websocketService from '../services/websocket';
import '../styles/VideoCanvas.css';

function VideoCanvas() {
  const canvasRef = useRef(null);
  const [fps, setFps] = useState(0);
  const lastFrameTime = useRef(Date.now());

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    websocketService.onVideoFrame((frameData) => {
      const now = Date.now();
      const elapsed = now - lastFrameTime.current;
      if (elapsed > 0) {
        setFps(Math.round(1000 / elapsed));
      }
      lastFrameTime.current = now;

      const img = new Image();
      img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
      };
      img.src = 'data:image/jpeg;base64,' + frameData;
    });

  }, []);

  return (
    <div className="video-canvas-container">
      <canvas ref={canvasRef} className="video-canvas" />
      <div className="fps-counter">{fps} FPS</div>
      <div className="instructions">
        <h3>Gesture Controls:</h3>
        <ul>
          <li>✌️ 1 finger = Draw</li>
          <li>✊ Fist = Erase</li>
          <li>✋ 2 fingers = Stop</li>
          <li>🤟 3 fingers = Next Color</li>
          <li>🖖 4 fingers = Previous Color</li>
        </ul>
      </div>
    </div>
  );
}

export default VideoCanvas;
