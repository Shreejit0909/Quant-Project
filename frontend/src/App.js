import React from 'react';
import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import { Toaster } from './components/ui/toaster';

function App() {
    return (
        <div className="App min-h-screen bg-[#0B0F14]">
            <BrowserRouter>
                <Navbar />
                <main className="pt-16">
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/analytics" element={<Analytics />} />
                        <Route path="/settings" element={<Settings />} />
                    </Routes>
                </main>
                <Toaster />
            </BrowserRouter>
        </div>
    );
}

export default App;
