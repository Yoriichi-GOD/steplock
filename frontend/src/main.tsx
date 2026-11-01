import React from 'react';
import {createRoot} from 'react-dom/client';
import {PublicRouter} from './PublicRouter';
import './styles/public.css';
import './styles/fonts.css';
createRoot(document.getElementById('root')!).render(<React.StrictMode><PublicRouter/></React.StrictMode>);
