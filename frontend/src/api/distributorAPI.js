import API from './axiosConfig';

export const distributorAPI = {
  getAvailableCrops: () => 
    API.get('/api/distributor/available-crops'),

  buyCrop: (cropId, quantity) => 
    API.post('/api/distributor/buy', { crop_id: cropId, quantity }),

  getMyPurchases: () => 
    API.get('/api/distributor/my-purchases'),

  getMySales: () => 
    API.get('/api/distributor/my-sales'),

  getInventory: () => 
    API.get('/api/distributor/inventory')
};