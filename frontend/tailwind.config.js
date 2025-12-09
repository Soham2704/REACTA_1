/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                dark: {
                    bg: "#0a0a0f",
                    card: "#13131f",
                    border: "#2a2a35",
                    accent: "#6366f1", // Indigo-500
                    success: "#10b981",
                    error: "#ef4444"
                }
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            }
        },
    },
    plugins: [],
}
