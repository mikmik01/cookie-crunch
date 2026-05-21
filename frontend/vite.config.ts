import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const apiTarget = env.API_PROXY_TARGET || "http://127.0.0.1:8000";
  return {
    plugins: [react(), tailwindcss()],
    server: {
      proxy: {
        "/query": {
          target: apiTarget,
          changeOrigin: true,
        },
        "/reports": {
          target: apiTarget,
          changeOrigin: true,
        },
        "/stats": {
          target: apiTarget,
          changeOrigin: true,
        },
      },
    },
  };
})