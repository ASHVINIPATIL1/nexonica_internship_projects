"""
Canvas Management Module
Handles drawing canvas with stroke-based rendering
"""

import cv2
import numpy as np
from typing import Tuple, Optional
from .stroke_manager import StrokeManager, Stroke
from .shape_recognizer import ShapeRecognizer
import config

class Canvas:
    def __init__(self, width: int, height: int):
        """
        Initialize canvas
        
        Args:
            width: Canvas width
            height: Canvas height
        """
        self.width = width
        self.height = height
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Stroke management
        self.stroke_manager = StrokeManager()
        self.shape_recognizer = ShapeRecognizer()
        
        # Drawing state
        self.prev_point = None
    
    def start_drawing(self, x: int, y: int, color: Tuple[int, int, int], thickness: int, mode: str):
        """
        Start a new drawing stroke
        
        Args:
            x, y: Starting point
            color: BGR color
            thickness: Brush thickness
            mode: 'draw' or 'erase'
        """
        stroke_type = 'erase' if mode == 'erase' else 'line'
        self.stroke_manager.start_new_stroke(color, thickness, stroke_type)
        self.stroke_manager.add_point_to_current_stroke(x, y)
        self.prev_point = (x, y)
    
    def continue_drawing(self, x: int, y: int, color: Tuple[int, int, int], thickness: int, mode: str):
        """
        Continue current drawing stroke
        
        Args:
            x, y: Current point
            color: BGR color
            thickness: Brush thickness
            mode: 'draw' or 'erase'
        """
        if self.prev_point is None:
            self.start_drawing(x, y, color, thickness, mode)
            return
        
        # Add point to current stroke
        self.stroke_manager.add_point_to_current_stroke(x, y)
        
        # Draw line on canvas immediately (for real-time feedback)
        if mode == 'erase':
            cv2.line(self.canvas, self.prev_point, (x, y), (0, 0, 0), thickness)
        else:
            cv2.line(self.canvas, self.prev_point, (x, y), color, thickness)
        
        self.prev_point = (x, y)
    
    def stop_drawing(self):
        """Stop current drawing stroke"""
        if self.prev_point is not None:
            self.stroke_manager.complete_current_stroke()
            self.prev_point = None
    
    def apply_shape_recognition(self):
        """
        Apply shape recognition to last stroke
        Replaces rough stroke with perfect shape
        
        Returns:
            bool: True if shape recognized and replaced, False otherwise
        """
        last_stroke = self.stroke_manager.get_last_completed_stroke()
        
        if last_stroke is None or len(last_stroke.points) < config.MIN_POINTS_FOR_SHAPE:
            print("⚠️ No stroke to recognize")
            return False
        
        # Get points as numpy array
        points = last_stroke.get_numpy_points()
        
        # Recognize shape
        shape_info = self.shape_recognizer.recognize_shape(points)
        
        if shape_info is None:
            return False
        
        # Create new stroke for perfect shape
        shape_stroke = Stroke(last_stroke.color, last_stroke.thickness, 'shape')
        shape_stroke.shape_info = shape_info  # Store shape info
        shape_stroke.complete()
        
        # Replace last stroke with shape stroke
        self.stroke_manager.replace_last_stroke_with_shape(shape_stroke)
        
        # Redraw entire canvas
        self._redraw_canvas()
        
        return True
    
    def undo(self) -> bool:
        """
        Undo last stroke
        
        Returns:
            bool: True if successful
        """
        success = self.stroke_manager.undo()
        if success:
            self._redraw_canvas()
        return success
    
    def redo(self) -> bool:
        """
        Redo last undone stroke
        
        Returns:
            bool: True if successful
        """
        success = self.stroke_manager.redo()
        if success:
            self._redraw_canvas()
        return success
    
    def clear(self):
        """Clear entire canvas"""
        self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.stroke_manager.clear_all()
        self.prev_point = None
    
    def _redraw_canvas(self):
        """Redraw entire canvas from stroke history"""
        # Clear canvas
        self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Redraw all strokes
        for stroke in self.stroke_manager.get_all_strokes():
            if hasattr(stroke, 'shape_info'):
                # It's a perfect shape
                self.shape_recognizer.draw_perfect_shape(
                    self.canvas,
                    stroke.shape_info,
                    stroke.color,
                    stroke.thickness
                )
            else:
                # It's a regular stroke - draw lines between points
                points = stroke.get_points()
                if len(points) < 2:
                    continue
                
                for i in range(len(points) - 1):
                    pt1 = points[i]
                    pt2 = points[i + 1]
                    
                    if stroke.stroke_type == 'erase':
                        cv2.line(self.canvas, pt1, pt2, (0, 0, 0), stroke.thickness)
                    else:
                        cv2.line(self.canvas, pt1, pt2, stroke.color, stroke.thickness)
    
    def get_canvas(self) -> np.ndarray:
        """Get current canvas image"""
        return self.canvas
    
    def can_undo(self) -> bool:
        """Check if undo is available"""
        return self.stroke_manager.can_undo()
    
    def can_redo(self) -> bool:
        """Check if redo is available"""
        return self.stroke_manager.can_redo()
    
    def save_as_png(self, filepath: str) -> bool:
        """
        Save canvas as PNG image
        
        Args:
            filepath: Path to save file
            
        Returns:
            bool: True if successful
        """
        try:
            cv2.imwrite(filepath, self.canvas)
            print(f"💾 Saved canvas to: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Error saving canvas: {e}")
            return False