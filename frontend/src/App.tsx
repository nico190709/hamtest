import React, { useState, useEffect, useRef } from 'react';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [userName, setUserName] = useState('');
  const [conversationStep, setConversationStep] = useState('greeting');
  const [isFirstMessage, setIsFirstMessage] = useState(true);
  const messagesEndRef = useRef(null);

  const BACKEND_URL = 'https://3000-firebase-hamtest-1751625756428.cluster-l6vkdperq5ebaqo3qy4ksvoqom.cloudworkstations.dev';

  // Scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initial greeting - GreenBot spezifisch
  useEffect(() => {
    const initialMessage = {
      id: Date.now(),
      text: "Hallo! 🌱 Ich bin GreenBot, dein Nachhaltigkeits-Assistent für den Büroalltag. Wie heißt du denn?",
      sender: 'bot',
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages([initialMessage]);
  }, []);

  const addMessage = (text, sender) => {
    const newMessage = {
      id: Date.now() + Math.random(),
      text,
      sender,
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleNameInput = (name) => {
    setUserName(name);
    setConversationStep('chatting');
    
    const responses = [
      `Schön dich kennenzulernen, ${name}! 🌿 Ich helfe dir gerne dabei, deinen Arbeitsalltag nachhaltiger zu gestalten.`,
      `Hallo ${name}! 🌱 Freut mich sehr! Lass uns gemeinsam für mehr Nachhaltigkeit im Büro sorgen.`,
      `Willkommen ${name}! 🌍 Wie kann ich dir heute bei nachhaltigen Entscheidungen helfen?`,
      `Hi ${name}! 🌿 Schön, dass du da bist! Bereit für grüne Tipps?`
    ];
    
    const randomResponse = responses[Math.floor(Math.random() * responses.length)];
    
    setTimeout(() => {
      addMessage(randomResponse, 'bot');
      setTimeout(() => {
        addMessage("Du kannst mich zu allem rund um Nachhaltigkeit im Büro fragen - von Reisen über Meetings bis hin zu Büromaterial! 🌱", 'bot');
        setIsFirstMessage(false);
      }, 1000);
    }, 500);
  };

  const sendToAI = async (message) => {
    try {
      const contextualMessage = isFirstMessage && userName 
        ? `Der Nutzer heißt ${userName}. Antworte freundlich und persönlich zu Nachhaltigkeit. Frage: ${message}`
        : `Beantworte die Nachhaltigkeitsfrage freundlich und konkret. Verwende NICHT den Namen des Nutzers. Frage: ${message}`;

      const result = await fetch(`${BACKEND_URL}/ai/sustainability/${encodeURIComponent(contextualMessage)}`, {
        credentials: 'include',
        headers: { 'Accept': 'application/json' }
      });
      
      const data = await result.json();
      
      if (data.error) {
        return "Entschuldigung, ich habe gerade technische Probleme. Kannst du es nochmal versuchen? 🌱";
      } else {
        try {
          const parsedResponse = typeof data.response === 'string' ? JSON.parse(data.response) : data.response;
          
          let responseText = '';
          
          if (typeof parsedResponse === 'object') {
            responseText = parsedResponse.answer || 
                          parsedResponse.antwort || 
                          parsedResponse.response || 
                          JSON.stringify(parsedResponse, null, 2);
          } else {
            responseText = parsedResponse;
          }
          
          // Entferne Namen aus der Antwort (außer bei der ersten Nachricht)
          if (!isFirstMessage && userName) {
            responseText = responseText
              .replace(new RegExp(`\\b${userName}\\b`, 'gi'), '')
              .replace(/^[,\s]+|[,\s]+$/g, '')
              .trim();
          }
          
          return responseText;
        } catch {
          let responseText = data.response;
          
          if (!isFirstMessage && userName) {
            responseText = responseText
              .replace(new RegExp(`\\b${userName}\\b`, 'gi'), '')
              .replace(/^[,\s]+|[,\s]+$/g, '')
              .trim();
          }
          
          return responseText;
        }
      }
    } catch (error) {
      return "Ups, da ist etwas schiefgelaufen. Versuche es gerne nochmal! 🌱";
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const userMessage = inputMessage.trim();
    addMessage(userMessage, 'user');
    setInputMessage('');
    setIsLoading(true);

    if (conversationStep === 'greeting') {
      handleNameInput(userMessage);
      setIsLoading(false);
      return;
    }

    try {
      const aiResponse = await sendToAI(userMessage);
      setTimeout(() => {
        addMessage(aiResponse, 'bot');
        setIsLoading(false);
        if (isFirstMessage) {
          setIsFirstMessage(false);
        }
      }, 500);
    } catch (error) {
      setTimeout(() => {
        addMessage("Entschuldigung, ich konnte deine Nachricht nicht verarbeiten. 😔", 'bot');
        setIsLoading(false);
      }, 500);
    }
  };

  const handleQuickReply = (message) => {
    setInputMessage(message);
  };

  // GreenBot spezifische Quick Replies
  const quickReplies = userName ? [
    "Nachhaltige Reise nach Berlin",
    "Umweltfreundliche Meeting-Optionen",
    "Nachhaltige Büromaterialien",
    "Grüne Kantinen-Tipps",
    "Energie sparen im Büro",
    "Papierlos arbeiten"
  ] : [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex flex-col">
      {/* Header - GreenBot Design */}
      <div className="bg-white shadow-sm p-4 border-b border-green-200">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center">
              <span className="text-white text-2xl">🌱</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">GreenBot</h1>
              <p className="text-sm text-gray-600">
                {userName ? `Nachhaltigkeits-Beratung für ${userName}` : 'Dein Nachhaltigkeits-Assistent'}
              </p>
            </div>
          </div>
          {userName && (
            <div className="text-sm text-gray-500 bg-green-50 px-3 py-1 rounded-full">
              🌿 <span className="font-medium text-green-700">{userName}</span>
            </div>
          )}
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                  message.sender === 'user'
                    ? 'bg-gradient-to-r from-green-500 to-blue-500 text-white'
                    : 'bg-white text-gray-800 shadow-sm border border-green-100'
                }`}
              >
                <p className="text-sm leading-relaxed">{message.text}</p>
                <p className={`text-xs mt-2 ${
                  message.sender === 'user' ? 'text-green-100' : 'text-gray-500'
                }`}>
                  {message.timestamp}
                </p>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-800 shadow-sm border border-green-100 px-4 py-3 rounded-lg">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                  <span className="text-sm text-gray-500">Denkt grün nach... 🌱</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Quick Replies - Nachhaltigkeits-Themen */}
      {quickReplies.length > 0 && (
        <div className="p-4 bg-white border-t border-green-200">
          <div className="max-w-4xl mx-auto">
            <p className="text-sm text-gray-600 mb-3 flex items-center">
              <span className="mr-2">🌿</span>
              Beliebte Nachhaltigkeits-Themen:
            </p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {quickReplies.map((reply, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickReply(reply)}
                  className="px-3 py-2 bg-green-50 hover:bg-green-100 text-green-700 text-sm rounded-lg transition-colors border border-green-200"
                >
                  {reply}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Input Form */}
      <div className="bg-white border-t border-green-200 p-4">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="flex space-x-4">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder={
                conversationStep === 'greeting' 
                  ? "Gib deinen Namen ein..." 
                  : "Frage mich zu Nachhaltigkeit im Büro..."
              }
              className="flex-1 px-4 py-3 border border-green-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !inputMessage.trim()}
              className="bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 disabled:from-gray-300 disabled:to-gray-300 text-white px-6 py-3 rounded-lg transition-all font-medium"
            >
              {isLoading ? '🌱' : '📤'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;