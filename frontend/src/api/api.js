// src/api/api.js
import axios from "axios";

const API = axios.create({
  baseURL: "https://foodchain-supplyy.onrender.com",, // Flask backend URL
});

// ---------- Farmer ----------
export const getCrops = () => API.get("/farmer/view_crops");
export const getFarmerCrops = (farmerId) => API.get(`/farmer/my_crops/${farmerId}`);
export const addCrop = (formData) => API.post("/farmer/add_crop", formData);

// ---------- Retailer ----------
// ---------- Retailer ----------
// ---------- Retailer ----------
export const getAvailableCrops = () => API.get("/api/retailer/crops");
export const buyCrop = (cropId, retailerId, quantity = 1) =>
  API.post("/api/retailer/buy", { 
    crop_id: cropId, 
    retailer_id: retailerId, 
    quantity: quantity 
  });
export const getRetailerPurchases = (retailerId) => 
  API.get(`/api/retailer/my-purchases?retailer_id=${retailerId}`);
export const getRetailerInventory = (retailerId) => 
  API.get(`/api/retailer/inventory?retailer_id=${retailerId}`);
// ---------- Distributor ----------
export const getDistributorCrops = () => API.get("/api/distributor/crops");

// ---------- Customer ----------
export const getCustomerCrops = () => API.get("/api/customer/crops");

// ---------- Traceability ----------
export const getCropHistory = (cropId) => API.get(`/trace/${cropId}`);

export default API;
