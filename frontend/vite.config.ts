import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
const apiOrigin=process.env.STEPLOCK_API_ORIGIN;
export default defineConfig({plugins: [react()], server: {port:62401,strictPort:true,proxy: apiOrigin?{'/api':apiOrigin}:undefined},preview:{port:62401,strictPort:true}});
