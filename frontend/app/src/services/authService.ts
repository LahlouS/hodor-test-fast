const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function loginUser(username: string, password: string) {
  const response = await fetch(`${API_URL}/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    credentials: 'include',
    body: new URLSearchParams({ username, password }),
  });
  if (!response.ok) throw new Error('Login failed');
  return response.json(); // { access_token, token_type }
}

export async function registerUser(username: string, email: string, password: string) {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password }),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err?.detail ?? 'Registration failed');
  }
  return response.json();
}

export async function refreshToken() {
  const response = await fetch(`${API_URL}/auth/refresh`, {
    credentials: 'include',
  });
  if (!response.ok) throw new Error('Refresh failed');
  return response.json(); // { access_token, token_type }
}

export async function logoutUser() {
  await fetch(`${API_URL}/auth/logout`, { credentials: 'include' });
}
