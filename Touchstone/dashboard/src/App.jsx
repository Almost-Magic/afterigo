import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './lib/theme';
import Layout from './components/Layout';
import ToastContainer from './components/Toast';
import Overview from './pages/Overview';
import Campaigns from './pages/Campaigns';
import Compare from './pages/Compare';
import Contacts from './pages/Contacts';
import ContactJourney from './pages/ContactJourney';

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Overview />} />
            <Route path="/campaigns" element={<Campaigns />} />
            <Route path="/compare" element={<Compare />} />
            <Route path="/contacts" element={<Contacts />} />
            <Route path="/contacts/:id" element={<ContactJourney />} />
          </Route>
        </Routes>
      </BrowserRouter>
      <ToastContainer />
    </ThemeProvider>
  );
}
