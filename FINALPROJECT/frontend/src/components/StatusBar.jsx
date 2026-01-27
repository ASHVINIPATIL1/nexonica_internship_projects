/**
 * StatusBar Component
 * Display current status
 */

import React from 'react';
import '../styles/StatusBar.css';

function StatusBar({ mode, color, brushSize, handDetected, canUndo, canRedo }) {
  return (
    <div className="status-bar">
      <div className="status-item">
        <span className="status-label">Mode:</span>
        <span className={`status-value mode-${mode.toLowerCase()}`}>{mode}</span>
      </div>
      
      <div className="status-item">
        <span className="status-label">Color:</span>
        <span className="status-value">{color.toUpperCase()}</span>
      </div>
      
      <div className="status-item">
        <span className="status-label">Brush:</span>
        <span className="status-value">{brushSize}px</span>
      </div>
      
      <div className="status-item">
        <span className="status-label">Hand:</span>
        <span className={`status-value ${handDetected ? 'detected' : 'not-detected'}`}>
          {handDetected ? '✓ Detected' : '✗ Not Detected'}
        </span>
      </div>
      
      <div className="status-item">
        <span className="status-label">History:</span>
        <span className="status-value">
          Undo: {canUndo ? 'YES' : 'NO'} | Redo: {canRedo ? 'YES' : 'NO'}
        </span>
      </div>
    </div>
  );
}

export default StatusBar;
