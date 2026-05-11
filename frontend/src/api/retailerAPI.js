import API from './axiosConfig';

export const retailerAPI = {
  getAvailableCrops: () => 
    API.get('/api/retailer/available-crops'),

  buyCrop: (cropId, quantity) => 
    API.post('/api/retailer/buy', { crop_id: cropId, quantity }),

  getMyPurchases: () => 
    API.get('/api/retailer/my-purchases'),

  getInventory: () => 
    API.get('/api/retailer/inventory')
};