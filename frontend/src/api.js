import axios from 'axios';

// Ensure this matches your FastAPI backend URL
const API_BASE_URL = 'http://127.0.0.1:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 300000, // 5 minutes for long AI generation
});

export const runPipeline = async (payload) => {
    try {
        const response = await api.post('/run_case', payload);
        return response.data;
    } catch (error) {
        console.error("Pipeline Error:", error);
        if (error.response) {
            // The server responded with a status code that falls out of the range of 2xx
            console.error("Server Response Data:", error.response.data);
            console.error("Server Response Status:", error.response.status);
            console.error("Server Response Headers:", error.response.headers);

            // Extract the specific detail message if available
            const errorDetail = error.response.data.detail || JSON.stringify(error.response.data);
            alert(`Server Error (${error.response.status}): ${errorDetail}`);
        } else if (error.request) {
            // The request was made but no response was received
            console.error("No response received:", error.request);
            alert("Network Error: No response from server. Is the backend running?");
        } else {
            // Something happened in setting up the request that triggered an Error
            console.error("Request Setup Error:", error.message);
            alert(`Client Error: ${error.message}`);
        }
        throw error;
    }
};

export const sendFeedback = async (payload) => {
    try {
        const response = await api.post('/feedback', payload);
        return response.data;
    } catch (error) {
        console.error("Feedback Error:", error);
        throw error;
    }
};

export default api;
