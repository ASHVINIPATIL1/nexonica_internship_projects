"""
Stroke Management Module
Tracks individual drawing strokes for undo/redo and shape recognition
"""

import numpy as np
from typing import List, Tuple, Optional
import config

class Stroke:
    """Represents a single drawing stroke"""
    
    def __init__(self, color: Tuple[int, int, int], thickness: int, stroke_type: str = 'line'):
        """
        Initialize a stroke
        
        Args:
            color: BGR color tuple
            thickness: Brush thickness
            stroke_type: 'line', 'shape', or 'erase'
        """
        self.points = []  # List of (x, y) coordinates
        self.color = color
        self.thickness = thickness
        self.stroke_type = stroke_type
        self.is_complete = False
    
    def add_point(self, x: int, y: int):
        """Add a point to the stroke"""
        self.points.append((x, y))
    
    def complete(self):
        """Mark stroke as complete"""
        self.is_complete = True
    
    def get_points(self) -> List[Tuple[int, int]]:
        """Get all points in the stroke"""
        return self.points
    
    def get_numpy_points(self) -> np.ndarray:
        """Get points as numpy array for shape recognition"""
        return np.array(self.points)
    
    def clear_points(self):
        """Clear all points (used when replacing with perfect shape)"""
        self.points = []


class StrokeManager:
    """Manages all strokes and stroke history"""
    
    def __init__(self):
        """Initialize stroke manager"""
        self.current_stroke = None
        self.all_strokes = []  # All strokes currently on canvas
        self.history = []  # For undo/redo
        self.redo_stack = []
    
    def start_new_stroke(self, color: Tuple[int, int, int], thickness: int, stroke_type: str = 'line'):
        """
        Start a new stroke
        
        Args:
            color: BGR color tuple
            thickness: Brush thickness
            stroke_type: 'line', 'shape', or 'erase'
        """
        self.current_stroke = Stroke(color, thickness, stroke_type)
    
    def add_point_to_current_stroke(self, x: int, y: int):
        """Add point to current stroke"""
        if self.current_stroke:
            self.current_stroke.add_point(x, y)
    
    def complete_current_stroke(self):
        """Complete current stroke and add to canvas"""
        if self.current_stroke and len(self.current_stroke.points) > 0:
            self.current_stroke.complete()
            self.all_strokes.append(self.current_stroke)
            
            # Add to history for undo
            self.history.append(self.current_stroke)
            
            # Limit history size
            if len(self.history) > config.MAX_HISTORY_SIZE:
                self.history.pop(0)
            
            # Clear redo stack when new stroke added
            self.redo_stack = []
            
            self.current_stroke = None
    
    def get_last_completed_stroke(self) -> Optional[Stroke]:
        """Get the most recent completed stroke"""
        if len(self.all_strokes) > 0:
            return self.all_strokes[-1]
        return None
    
    def replace_last_stroke_with_shape(self, shape_stroke: Stroke):
        """
        Replace last stroke with a perfect shape
        
        Args:
            shape_stroke: New stroke representing perfect shape
        """
        if len(self.all_strokes) > 0:
            # Remove last stroke
            removed_stroke = self.all_strokes.pop()
            
            # Add shape stroke
            self.all_strokes.append(shape_stroke)
            
            # Update history
            if removed_stroke in self.history:
                idx = self.history.index(removed_stroke)
                self.history[idx] = shape_stroke
    
    def undo(self) -> bool:
        """
        Undo last stroke
        
        Returns:
            bool: True if undo successful, False if nothing to undo
        """
        if len(self.history) > 0:
            # Remove last stroke from history
            undone_stroke = self.history.pop()
            
            # Add to redo stack
            self.redo_stack.append(undone_stroke)
            
            # Remove from canvas
            if undone_stroke in self.all_strokes:
                self.all_strokes.remove(undone_stroke)
            
            print("⬅️ Undo")
            return True
        
        print("⚠️ Nothing to undo")
        return False
    
    def redo(self) -> bool:
        """
        Redo last undone stroke
        
        Returns:
            bool: True if redo successful, False if nothing to redo
        """
        if len(self.redo_stack) > 0:
            # Get stroke from redo stack
            redone_stroke = self.redo_stack.pop()
            
            # Add back to history
            self.history.append(redone_stroke)
            
            # Add back to canvas
            self.all_strokes.append(redone_stroke)
            
            print("➡️ Redo")
            return True
        
        print("⚠️ Nothing to redo")
        return False
    
    def clear_all(self):
        """Clear all strokes"""
        self.all_strokes = []
        self.history = []
        self.redo_stack = []
        self.current_stroke = None
        print("🗑️ Canvas cleared")
    
    def can_undo(self) -> bool:
        """Check if undo is available"""
        return len(self.history) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available"""
        return len(self.redo_stack) > 0
    
    def get_all_strokes(self) -> List[Stroke]:
        """Get all strokes on canvas"""
        return self.all_strokes
