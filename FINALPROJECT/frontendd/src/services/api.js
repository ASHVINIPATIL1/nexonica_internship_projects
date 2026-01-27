/**
 * API Service
 * HTTP requests to backend
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const getStatus = async () => {
  try {
    const response = await api.get('/api/status');
    return response.data;
  } catch (error) {
    console.error('Error getting status:', error);
    throw error;
  }
};

export const clearCanvas = async () => {
  try {
    const response = await api.post('/api/clear');
    return response.data;
  } catch (error) {
    console.error('Error clearing canvas:', error);
    throw error;
  }
};

export const undo = async () => {
  try {
    const response = await api.post('/api/undo');
    return response.data;
  } catch (error) {
    console.error('Error undo:', error);
    throw error;
  }
};

export const redo = async () => {
  try {
    const response = await api.post('/api/redo');
    return response.data;
  } catch (error) {
    console.error('Error redo:', error);
    throw error;
  }
};

export const perfectShape = async () => {
  try {
    const response = await api.post('/api/perfect-shape');
    return response.data;
  } catch (error) {
    console.error('Error perfect shape:', error);
    throw error;
  }
};

export const changeColor = async (color) => {
  try {
    const response = await api.post('/api/color', { color });
    return response.data;
  } catch (error) {
    console.error('Error changing color:', error);
    throw error;
  }
};

export const changeBrushSize = async (size) => {
  try {
    const response = await api.post('/api/brush-size', { size });
    return response.data;
  } catch (error) {
    console.error('Error changing brush size:', error);
    throw error;
  }
};

export const saveCanvas = async () => {
  try {
    const response = await api.post('/api/save');
    return response.data;
  } catch (error) {
    console.error('Error saving canvas:', error);
    throw error;
  }
};
