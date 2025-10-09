import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App.tsx';
import 'bootstrap/dist/css/bootstrap.min.css';
import { AvatarProvider } from './context/AvatarContext.tsx';
import { PromptProvider } from './context/PromptContext.tsx';
import { SceneSettingsProvider } from './context/SceneSettingsContext.tsx';
import { ModeProvider } from './context/ModeContext.tsx';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <ModeProvider>
        <AvatarProvider>
          <PromptProvider>
            <SceneSettingsProvider>
              <App />
            </SceneSettingsProvider>
          </PromptProvider>
        </AvatarProvider>
      </ModeProvider>
    </BrowserRouter>
  </React.StrictMode>,
);

