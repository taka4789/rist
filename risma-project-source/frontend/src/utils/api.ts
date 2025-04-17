import axios from 'axios';

// APIのベースURL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// APIクライアントの設定
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエストインターセプター
apiClient.interceptors.request.use(
  (config) => {
    // ブラウザ環境の場合のみlocalStorageを使用
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// レスポンスインターセプター
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // 401エラーかつリフレッシュトークンがある場合、トークンをリフレッシュ
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh-token`, {
            refresh_token: refreshToken,
          });
          
          const { access_token } = response.data;
          localStorage.setItem('token', access_token);
          
          // 新しいトークンでリクエストを再試行
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return axios(originalRequest);
        }
      } catch (refreshError) {
        // リフレッシュに失敗した場合はログアウト
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// API関数
const api = {
  // 認証関連
  auth: {
    login: (credentials) => apiClient.post('/api/auth/login', credentials),
    register: (userData) => apiClient.post('/api/auth/register', userData),
    refreshToken: (refreshToken) => apiClient.post('/api/auth/refresh-token', { refresh_token: refreshToken }),
    testToken: () => apiClient.post('/api/auth/test-token'),
  },
  
  // ユーザー関連
  users: {
    getProfile: () => apiClient.get('/api/users/me'),
    updateProfile: (userData) => apiClient.put('/api/users/me', userData),
    getAll: () => apiClient.get('/api/users'),
    getById: (id) => apiClient.get(`/api/users/${id}`),
    create: (userData) => apiClient.post('/api/users', userData),
    update: (id, userData) => apiClient.put(`/api/users/${id}`, userData),
    delete: (id) => apiClient.delete(`/api/users/${id}`),
  },
  
  // 検索関連
  search: {
    keyword: (params, listId) => apiClient.post(`/api/search/keyword?list_id=${listId}`, params),
    industryLocation: (params, listId) => apiClient.post(`/api/search/industry-location?list_id=${listId}`, params),
    getJobs: (limit) => apiClient.get(`/api/search/jobs?limit=${limit || ''}`),
    getJobById: (id) => apiClient.get(`/api/search/jobs/${id}`),
    cancelJob: (id) => apiClient.post(`/api/search/jobs/${id}/cancel`),
  },
  
  // リスト関連
  lists: {
    getAll: (limit) => apiClient.get(`/api/lists?limit=${limit || ''}`),
    getById: (id) => apiClient.get(`/api/lists/${id}`),
    create: (listData) => apiClient.post('/api/lists', listData),
    update: (id, listData) => apiClient.put(`/api/lists/${id}`, listData),
    delete: (id) => apiClient.delete(`/api/lists/${id}`),
    export: (id) => apiClient.get(`/api/lists/${id}/export`, { responseType: 'blob' }),
  },
  
  // 監査ログ関連
  audit: {
    getLogs: (params) => apiClient.get('/api/audit/logs', { params }),
  },
  
  // 場所関連
  location: {
    getPrefectures: () => apiClient.get('/api/location/prefectures'),
    getCities: (prefecture) => apiClient.get(`/api/location/cities?prefecture=${prefecture}`),
  },
};

export default api;
