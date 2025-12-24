const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

type RequestMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

interface RequestOptions {
    method?: RequestMethod;
    headers?: Record<string, string>;
    body?: any;
}

export async function fetchAPI<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const { method = "GET", headers = {}, body } = options;

    const config: RequestInit = {
        method,
        headers: {
            "Content-Type": "application/json",
            ...headers,
        },
    };

    // Auto-attach token if available
    if (typeof window !== 'undefined') {
        const token = localStorage.getItem('token');
        if (token) {
            (config.headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
        }
    }

    if (body) {
        config.body = JSON.stringify(body);
    }

    // Ensure endpoint starts with / if not present
    const path = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;

    try {
        const response = await fetch(`${API_URL}${path}`, config);

        if (!response.ok) {
            // Try to parse error message
            let errorMessage = `API Error: ${response.statusText}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.message || errorMessage;
            } catch (e) {
                // Ignore JSON parse error if body is not JSON
            }
            throw new Error(errorMessage);
        }

        // Handle 204 No Content
        if (response.status === 204) {
            return {} as T;
        }

        return await response.json();
    } catch (error) {
        console.error(`API Request Failed (${method} ${path}):`, error);
        throw error;
    }
}
