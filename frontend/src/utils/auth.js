// Token management utilities

/**
 * Get the access token from localStorage
 */
export const getToken = () => {
  return localStorage.getItem('access_token');
};

/**
 * Get the refresh token from localStorage
 */
export const getRefreshToken = () => {
  return localStorage.getItem('refresh_token');
};

/**
 * Save both access and refresh tokens
 */
export const setTokens = (access, refresh) => {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
};

/**
 * Remove all authentication tokens
 */
export const clearTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = () => {
  return !!getToken();
};

/**
 * Get current user from localStorage
 */
export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

/**
 * Save current user to localStorage
 */
export const setCurrentUser = (user) => {
  localStorage.setItem('user', JSON.stringify(user));
};
