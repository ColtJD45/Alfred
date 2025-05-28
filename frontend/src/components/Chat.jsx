//alfred_v0.1.3/frontend/src/Chat.jsx
import React, { useState, useRef, useEffect } from 'react';
import alfredLogo from '../assets/Alfred.png';
import UserIdModal from './UserIdModal';

function Chat() {
  const [userId, setUserId] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [showUserIdModal, setShowUserIdModal] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const baseUrl = import.meta.env.VITE_API_BASE_URL;

  

  const updateMessages = (newMessages) => {
    const limitedMessages = newMessages.slice(-20); // keep only last 20
    setMessages(limitedMessages); // Update the state with the limited messages
    if (sessionId) {
      localStorage.setItem(`messages_${sessionId}`, JSON.stringify(limitedMessages)); // Save the messages to localStorage
    }
  };

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch(`${baseUrl}/history?user_id=default`);
        const data = await res.json();
        if (data && Array.isArray(data)) {
          setMessages(data); // Replace existing chat state with history
        }
      } catch (err) {
        console.error("Failed to load chat history:", err);
      }
    };
  
    fetchHistory();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (sessionId && messages.length > 0) {
      const recentMessages = messages.slice(-20); // keep only the last 20
      localStorage.setItem(`messages_${sessionId}`, JSON.stringify(recentMessages));
    }
  }, [messages, sessionId]);

  useEffect(() => {
    const storedUserId = localStorage.getItem('userId');
    const storedSessionId = localStorage.getItem('sessionId');
  
    if (!storedUserId || !storedSessionId) {
      setShowUserIdModal(true);
    } else {
      setUserId(storedUserId);
      setSessionId(storedSessionId);

      const savedMessages = localStorage.getItem(`messages_${storedSessionId}`);
      if (savedMessages) {
        setMessages(JSON.parse(savedMessages));
      } else {
        // fallback to history fetch
        fetch(`${baseUrl}/history?user_id=${storedUserId}`)
          .then((res) => res.json())
          .then((data) => {
            if (Array.isArray(data)) setMessages(data);
          })
          .catch((err) => console.error("Failed to load chat history:", err));
      }
    }
  }, []);

  const handleUserIdSubmit = (userId) => {
    const newSessionId = userId;
    localStorage.setItem('userId', userId);
    localStorage.setItem('sessionId', newSessionId);
    setUserId(userId);
    setSessionId(newSessionId);
    setShowUserIdModal(false);
  };
  

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleInputChange = (event) => {
    setInputValue(event.target.value);
  };

  const sendMessageToAI = async (userMessage) => {
    if (!userId) {
      console.error('User ID not set');
      return;
    }
    const sessionId = localStorage.getItem('sessionId')

    try {
      const response = await fetch(`${baseUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          content: userMessage,
          user_id: userId,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Server error:', errorData);
        throw new Error(`Server responded with ${response.status}: ${errorData.detail || 'Unknown error'}`);
      }

      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error('Error:', error);
      return 'Sorry, I encountered an error. Please try again.';
    }
};

  const handleSendMessage = async () => {
    if (inputValue.trim() !== '') {
      // Add user message
      const userMessage = inputValue;
      updateMessages([...messages, { text: userMessage, sender: 'user' }]);
      setInputValue('');
      setIsLoading(true);

      // Get AI response
      const aiResponse = await sendMessageToAI(userMessage);
      updateMessages([...messages, { text: userMessage, sender: 'user' }, { text: aiResponse, sender: 'ai' }]);
      setIsLoading(false);
      inputRef.current.focus();
    }
  };

  if (showUserIdModal) {
    return <UserIdModal onSubmit={handleUserIdSubmit} />;
  }
  

  return (
    <div className="h-screen bg-black flex flex-col relative">
      <header className="w-full text-center py-8">
        <h1 className="text-6xl font-extrabold text-[#fac99c] mb-4 font-tangerine-regular tracking-wider">
          Alfred
        </h1>
        <img
          src={alfredLogo}
          alt="Alfred Logo"
          className="mx-auto w-36 h-36 object-cover rounded-3xl shadow-lg"
        />
      </header>

      {/* Chat area */}
      <main className="flex-1 overflow-y-auto overflow-x-hidden px-4 pb-24">
        <div className="max-w-[600px] mx-auto space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex items-start ${
                message.sender === 'user' ? 'justify-end' : ''
              }`}
            >
              <div
                className={`${
                  message.sender === 'user'
                    ? 'bg-[#2c1d0e] rounded-tr-sm'
                    : 'bg-[#905b29] rounded-tl-sm'
                } text-white font-bold rounded-2xl px-4 py-2 max-w-[80%]`}
              >
                {message.text}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex items-start">
              <div className="bg-[#905b29] text-white font-bold rounded-2xl rounded-tl-sm px-4 py-2">
                Butlering...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Gradient fade overlay - positioned from bottom of screen */}
      <div
        className="pointer-events-none fixed left-0 right-0 bottom-0"
        style={{
          height: '150px', // Made taller to cover more area
          background: 'linear-gradient(to top, black, transparent)',
          zIndex: 5
        }}
      />

      {/* Input bubble */}
      <form
        className="fixed bottom-6 left-1/2 -translate-x-1/2 w-full md:w-[600px] md:mx-auto bg-black 
          px-4 py-4 flex items-center gap-2"
        style={{ zIndex: 10 }}
        onSubmit={(e) => {
          e.preventDefault();
          handleSendMessage();
        }}
      >
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          disabled={isLoading}
          placeholder="How may I assist you?..."
          className="flex-1 rounded-full px-4 py-3 bg-black text-white placeholder-gray-400 
            focus:outline-none focus:ring-1 focus:ring-[#934822] transition appearance-none border-2 border-[#472d15]"
          style={{
            WebkitAppearance: 'none',
            backgroundColor: 'black'
          }}
        />
        <button
          type="submit"
          disabled={isLoading}
          className="ml-0 w-14 h-14 rounded-full bg-translucent shadow-md flex items-center justify-center">
          <i className="fa-regular fa-bell text-[#ffab5d] text-3xl transition-all duration-300 active:text-4xl"></i>
        </button>
      </form>
    </div>
  );
}

export default Chat;