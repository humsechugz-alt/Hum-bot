import React, { useState } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  emotion?: {
    label: string;
    confidence: number;
  };
  timestamp: string;
}

const PERSONALITIES = [
  { id: 'friendly', name: 'Friendly', emoji: '😊' },
  { id: 'professional', name: 'Professional', emoji: '💼' },
  { id: 'creative', name: 'Creative', emoji: '🎨' },
  { id: 'technical', name: 'Technical', emoji: '⚙️' },
  { id: 'supportive', name: 'Supportive', emoji: '💙' },
];

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [personality, setPersonality] = useState('friendly');
  const [conversationId, setConversationId] = useState<string | null>(null);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          conversation_id: conversationId,
          personality,
          include_emotion: true,
        }),
      });

      const data = await response.json();
      setConversationId(data.conversation_id);

      const aiMessage: Message = {
        id: data.message.id,
        role: 'assistant',
        content: data.message.content,
        emotion: data.emotion,
        timestamp: data.message.created_at,
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch {
      setMessages(prev => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: 'Connection error. Please ensure the HUGZ AI backend is running on port 8000.',
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#0f172a', color: '#e2e8f0', fontFamily: 'system-ui, sans-serif' }}>
      {/* Header */}
      <header style={{ padding: '16px 24px', borderBottom: '1px solid #1e293b', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ fontSize: '32px' }}>🤗</div>
          <div>
            <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 700, background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              HUGZ AI
            </h1>
            <p style={{ margin: 0, fontSize: '12px', color: '#64748b' }}>Your Intelligent AI Companion</p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          {PERSONALITIES.map(p => (
            <button
              key={p.id}
              onClick={() => setPersonality(p.id)}
              style={{
                padding: '6px 12px',
                borderRadius: '20px',
                border: personality === p.id ? '2px solid #3b82f6' : '1px solid #334155',
                background: personality === p.id ? '#1e3a5f' : 'transparent',
                color: '#e2e8f0',
                cursor: 'pointer',
                fontSize: '13px',
              }}
            >
              {p.emoji} {p.name}
            </button>
          ))}
        </div>
      </header>

      {/* Messages */}
      <main style={{ maxWidth: '800px', margin: '0 auto', padding: '24px', minHeight: 'calc(100vh - 180px)', display: 'flex', flexDirection: 'column' }}>
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', marginTop: '80px' }}>
            <div style={{ fontSize: '64px', marginBottom: '16px' }}>🤗</div>
            <h2 style={{ fontSize: '28px', fontWeight: 600, marginBottom: '8px' }}>Welcome to HUGZ AI</h2>
            <p style={{ color: '#64748b', maxWidth: '500px', margin: '0 auto' }}>
              Your intelligent AI companion with emotion detection, voice interaction,
              cybersecurity protection, and smart automation. Start a conversation below.
            </p>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginTop: '24px', flexWrap: 'wrap' }}>
              {['Tell me about yourself', 'How can you help me?', 'What security features do you have?', 'Show me automation options'].map(suggestion => (
                <button
                  key={suggestion}
                  onClick={() => { setInput(suggestion); }}
                  style={{ padding: '8px 16px', borderRadius: '20px', border: '1px solid #334155', background: '#1e293b', color: '#94a3b8', cursor: 'pointer', fontSize: '13px' }}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map(msg => (
          <div
            key={msg.id}
            style={{
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
              marginBottom: '16px',
            }}
          >
            <div style={{
              maxWidth: '70%',
              padding: '12px 16px',
              borderRadius: '16px',
              background: msg.role === 'user' ? '#3b82f6' : '#1e293b',
              border: msg.role === 'assistant' ? '1px solid #334155' : 'none',
            }}>
              <p style={{ margin: 0, lineHeight: 1.6 }}>{msg.content}</p>
              {msg.emotion && (
                <div style={{ marginTop: '8px', fontSize: '12px', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <span>Detected emotion: {msg.emotion.label}</span>
                  <span>({Math.round(msg.emotion.confidence * 100)}%)</span>
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '16px' }}>
            <div style={{ padding: '12px 16px', borderRadius: '16px', background: '#1e293b', border: '1px solid #334155' }}>
              <p style={{ margin: 0, color: '#64748b' }}>HUGZ AI is thinking...</p>
            </div>
          </div>
        )}
      </main>

      {/* Input */}
      <footer style={{ position: 'fixed', bottom: 0, left: 0, right: 0, padding: '16px', background: '#0f172a', borderTop: '1px solid #1e293b' }}>
        <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', gap: '8px' }}>
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && sendMessage()}
            placeholder="Talk to HUGZ AI..."
            style={{
              flex: 1,
              padding: '12px 16px',
              borderRadius: '24px',
              border: '1px solid #334155',
              background: '#1e293b',
              color: '#e2e8f0',
              fontSize: '15px',
              outline: 'none',
            }}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            style={{
              padding: '12px 24px',
              borderRadius: '24px',
              border: 'none',
              background: isLoading || !input.trim() ? '#334155' : '#3b82f6',
              color: 'white',
              cursor: isLoading || !input.trim() ? 'not-allowed' : 'pointer',
              fontSize: '15px',
              fontWeight: 600,
            }}
          >
            Send
          </button>
        </div>
      </footer>
    </div>
  );
}

export default App;
