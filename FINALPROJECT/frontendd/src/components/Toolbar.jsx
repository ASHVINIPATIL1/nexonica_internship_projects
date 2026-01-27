/**
 * Toolbar Component
 * Control buttons and settings
 */

import React from 'react';
import '../styles/Toolbar.css';

const COLORS = ['red', 'blue', 'green', 'yellow', 'purple', 'white'];

function Toolbar({
  onClearCanvas,
  onUndo,
  onRedo,
  onPerfectShape,
  onChangeColor,
  onChangeBrushSize,
  onSaveCanvas,
  currentColor,
  brushSize,
  canUndo,
  canRedo
}) {
  
  const handleBrushSizeChange = (e) => {
    onChangeBrushSize(parseInt(e.target.value));
  };

  return (
    <div className="toolbar">
      <div className="toolbar-section">
        <h3>Colors</h3>
        <div className="color-picker">
          {COLORS.map((color) => (
            <button
              key={color}
              className={`color-btn ${currentColor === color ? 'active' : ''}`}
              style={{ 
                backgroundColor: color === 'white' ? '#fff' : color,
                border: color === 'white' ? '2px solid #333' : 'none'
              }}
              onClick={() => onChangeColor(color)}
              title={color}
            >
              {currentColor === color && '✓'}
            </button>
          ))}
        </div>
      </div>

      <div className="toolbar-section">
        <h3>Brush Size: {brushSize}px</h3>
        <input
          type="range"
          min="2"
          max="30"
          value={brushSize}
          onChange={handleBrushSizeChange}
          className="brush-slider"
        />
      </div>

      <div className="toolbar-section">
        <h3>Actions</h3>
        <div className="action-buttons">
          <button 
            className="btn btn-undo" 
            onClick={onUndo}
            disabled={!canUndo}
            title="Undo"
          >
            ↩️ Undo
          </button>
          <button 
            className="btn btn-redo" 
            onClick={onRedo}
            disabled={!canRedo}
            title="Redo"
          >
            ↪️ Redo
          </button>
          <button 
            className="btn btn-shape" 
            onClick={onPerfectShape}
            title="Perfect Shape"
          >
            ✨ Perfect Shape
          </button>
          <button 
            className="btn btn-clear" 
            onClick={onClearCanvas}
            title="Clear Canvas"
          >
            🗑️ Clear
          </button>
          <button 
            className="btn btn-save" 
            onClick={onSaveCanvas}
            title="Save"
          >
            💾 Save
          </button>
        </div>
      </div>
    </div>
  );
}

export default Toolbar;
