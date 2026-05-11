import API from './axiosConfig';

export const farmerAPI = {
  addCrop: (formData) => 
    API.post('/api/farmer/crops', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),

  getMyCrops: () => 
    API.get('/api/farmer/my-crops'),

  getAvailableCrops: () => 
    API.get('/api/farmer/available-crops')
};