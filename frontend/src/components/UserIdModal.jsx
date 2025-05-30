//alfred/frontend/src/UserIdModal.jsx
import React, { useState } from 'react';

const UserIdModal = ({ onSubmit }) => {
    const [userId, setUserId] = useState('');
    const [error, setError] = useState('');
  
    const handleSubmit = (e) => {
      e.preventDefault();
      if (!userId || userId.trim() === '') {
        setError('Please enter a valid name');
        return;
      }
      onSubmit(userId.trim());
    };
  
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-[#2c1d0e] p-6 rounded-2xl shadow-xl max-w-sm w-full mx-4">
          <h2 className="text-2xl font-bold text-[#fac99c] mb-4">Welcome to Alfred</h2>
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label htmlFor="userId" className="block text-[#fac99c] mb-2">
                Please enter your name
              </label>
              <input
                type="text"
                id="userId"
                value={userId}
                onChange={(e) => {
                  setUserId(e.target.value);
                  setError('');
                }}
                className="w-full px-4 py-2 rounded-lg bg-black text-white border-2 border-[#472d15] focus:outline-none focus:ring-1 focus:ring-[#934822]"
                autoFocus
              />
              {error && <p className="text-red-500 mt-2 text-sm">{error}</p>}
            </div>
            <button
              type="submit"
              className="w-full bg-[#905b29] text-white py-2 rounded-lg hover:bg-[#734820] transition-colors"
            >
              Continue
            </button>
          </form>
        </div>
      </div>
    );
  };

export default UserIdModal;