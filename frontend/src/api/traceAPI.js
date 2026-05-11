import API from './axiosConfig';

export const traceAPI = {
  getCropJourney: (traceId) => 
    API.get(`/api/trace/${traceId}`),

  getBlockDetails: (blockHash) => 
    API.get(`/api/trace/blockchain/${blockHash}`)
};