import { fetchAPI } from "../api";

// Define Types (Interfaces) based on Backend Schemas
export interface UserCreate {
    email: string;
    password: string;
    full_name?: string;
}

export interface UserLogin {
    username: string; // The backend uses OAuth2PasswordRequestForm which expects 'username', usually mapped to email
    password: string;
}

export interface Token {
    access_token: string;
    token_type: string;
}

export const authService = {
    // Signup
    signup: async (userData: UserCreate) => {
        return await fetchAPI<any>("/users/", {
            method: "POST",
            body: userData,
        });
    },

    // Login
    // Note: OAuth2 form data is usually sent as application/x-www-form-urlencoded
    // But let's check if our backend supports JSON or if we need to format it.
    // Standard FastAPI OAuth2 expects form data.
    login: async (credentials: UserLogin) => {
        const formData = new URLSearchParams();
        formData.append("username", credentials.username);
        formData.append("password", credentials.password);

        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/login/access_token`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: formData.toString(),
        });

        if (!response.ok) {
            throw new Error("Login failed");
        }

        return await response.json() as Token;
    },

    getCurrentUser: async () => {
        return await fetchAPI<any>('/users/me', {
            method: 'GET',
        });
    }
};
