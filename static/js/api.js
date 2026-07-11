// API Configuration
const API_BASE_URL = '/api/';
const API = {
    auth: {
        login: `${API_BASE_URL}auth/login/`,
        register: `${API_BASE_URL}auth/register/`,
        currentUser: `${API_BASE_URL}auth/current_user/`,
    },
    users: `${API_BASE_URL}users/`,
    students: `${API_BASE_URL}students/`,
    courses: `${API_BASE_URL}courses/`,
    classes: `${API_BASE_URL}classes/`,
    applications: `${API_BASE_URL}applications/`,
    departments: `${API_BASE_URL}departments/`,
};

// Auth Token Management
function getAuthToken() {
    return localStorage.getItem('access_token');
}

function setAuthToken(token) {
    localStorage.setItem('access_token', token);
}

function removeAuthToken() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
}

// API Request Helper
async function apiRequest(url, method = 'GET', data = null) {
    const headers = {
        'Content-Type': 'application/json',
    };
    const token = getAuthToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const options = {
        method,
        headers,
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    const response = await fetch(url, options);
    const result = await response.json();
    
    if (!response.ok) {
        if (response.status === 401) {
            removeAuthToken();
            window.location.href = '/login/';
        }
        throw { status: response.status, data: result };
    }
    
    return result;
}

// Auth Functions
async function login(username, password) {
    try {
        const result = await apiRequest(API.auth.login, 'POST', { username, password });
        setAuthToken(result.access);
        localStorage.setItem('refresh_token', result.refresh);
        localStorage.setItem('user', JSON.stringify(result.user));
        return { success: true, user: result.user };
    } catch (error) {
        return { success: false, error: error.data };
    }
}

async function logout() {
    removeAuthToken();
    localStorage.removeItem('user');
    window.location.href = '/login/';
}

function getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

// Student Functions
async function getStudents(params = {}) {
    const query = new URLSearchParams(params).toString();
    return await apiRequest(`${API.students}?${query}`);
}

async function getStudent(id) {
    return await apiRequest(`${API.students}${id}/`);
}

async function createStudent(data) {
    return await apiRequest(API.students, 'POST', data);
}

async function updateStudent(id, data) {
    return await apiRequest(`${API.students}${id}/`, 'PUT', data);
}

// Course Functions
async function getCourses(params = {}) {
    const query = new URLSearchParams(params).toString();
    return await apiRequest(`${API.courses}?${query}`);
}

// Application Functions
async function getApplications(params = {}) {
    const query = new URLSearchParams(params).toString();
    return await apiRequest(`${API.applications}?${query}`);
}

async function submitApplication(data) {
    return await apiRequest(API.applications, 'POST', data);
}

// Export functions
window.API = {
    login,
    logout,
    getCurrentUser,
    getStudents,
    getStudent,
    createStudent,
    updateStudent,
    getCourses,
    getApplications,
    submitApplication,
    getAuthToken,
    setAuthToken,
    removeAuthToken,
};