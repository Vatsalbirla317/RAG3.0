import React from 'react';

function App() {
  return (
    <div className="min-h-screen bg-black text-green-400 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-bold mb-4">⚡ CodeMatrix ⚡</h1>
        <p className="text-2xl mb-4">Your Code's Digital Ghost</p>
        <p className="text-lg mb-8">✅ Deployment Test Successful!</p>
        <div className="text-sm opacity-60">
          <p>Environment: {import.meta.env.MODE}</p>
          <p>API URL: {import.meta.env.VITE_API_URL || 'Not set'}</p>
          <p>Build Time: {new Date().toISOString()}</p>
        </div>
      </div>
    </div>
  );
}

export default App;