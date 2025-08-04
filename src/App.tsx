import { Routes, Route } from 'react-router-dom';
import HomePage from './components/HomePage';
import AvatarUploader from './components/AvatarUploader';
import Prompt from './components/Prompt';
import FurtherInfo from './components/FurtherInfo';
import Preview from './components/Preview';
import Generate from './components/Generate';

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/upload" element={<AvatarUploader />} />
      <Route path="/prompt" element={<Prompt />} />
      <Route path="/scene" element={<FurtherInfo />} />
      <Route path='/preview' element={<Preview />} />
      <Route path='/generate' element={<Generate />} />
    </Routes>
  );
}

export default App;
