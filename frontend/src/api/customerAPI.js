import API from './axiosConfig';

export const customerAPI = {
  getAvailableCrops: () => 
    API.get('/api/customer/available-crops'),

  buyCrop: (cropId, quantity) => 
    API.post('/api/customer/buy', { crop_id: cropId, quantity }),

  getMyPurchases: () => 
    API.get('/api/customer/my-purchases')
};