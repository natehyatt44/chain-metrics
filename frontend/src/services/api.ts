import axios from 'axios';
import { Metric } from '../types/metrics';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080/api';

export const fetchHederaTxCount = async (): Promise<Metric[]> => {
  const response = await axios.get(`${API_BASE_URL}/metrics/hedera/tx-count`);
  return response.data;
};

export const fetchHederaUSDC = async (): Promise<Metric[]> => {
  const response = await axios.get(`${API_BASE_URL}/metrics/hedera/usdc-minted`);
  return response.data;
};

export const fetchGreedFearIndex = async (): Promise<Metric[]> => {
  const response = await axios.get(`${API_BASE_URL}/metrics/crypto/greed-fear`);
  return response.data;
}; 