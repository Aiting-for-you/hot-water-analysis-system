import axios from 'axios';

const API_URL = '/api/weather';

// Setup axios to include the token from localStorage
const api = axios.create();

api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

export const searchCities = async (cityName: string) => {
  const response = await api.get(`${API_URL}/search`, {
    params: { city: cityName }
  });
  return response.data;
};

export const getHourlyWeather = async (areacode: string) => {
  const response = await api.get(`${API_URL}/hourly`, {
    params: { areacode }
  });
  return response.data;
}; 