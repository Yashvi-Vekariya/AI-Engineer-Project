import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import Groq from 'groq-sdk';
import path from 'path';
import { fileURLToPath } from 'url';

// Fix for __dirname in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Enhanced CORS configuration
app.use(cors({
  origin: ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5500'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'Accept']
}));

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Serve static files from frontend directory
app.use(express.static(path.join(__dirname, '../frontend')));

// Initialize Groq
const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY
});

// Request logging middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  console.log('Request Body:', req.body);
  next();
});

// Rate limiting storage
const rateLimit = new Map();

// Simple rate limiting middleware
const rateLimiter = (req, res, next) => {
  const ip = req.ip;
  const now = Date.now();
  const windowStart = now - 60000; // 1 minute window
  
  if (!rateLimit.has(ip)) {
    rateLimit.set(ip, []);
  }
  
  const requests = rateLimit.get(ip).filter(time => time > windowStart);
  rateLimit.set(ip, requests);
  
  if (requests.length >= 10) { // 10 requests per minute
    return res.status(429).json({
      error: 'Rate limit exceeded. Please try again in a minute.'
    });
  }
  
  requests.push(now);
  next();
};

// ✅ FIXED: Chat endpoint with proper route definition
app.post('/api/chat', rateLimiter, async (req, res) => {
  try {
    console.log('Received chat request body:', req.body);
    
    const { messages, model = 'llama-3.1-8b-instant' } = req.body;

    // Validate request
    if (!messages || !Array.isArray(messages)) {
      return res.status(400).json({ 
        error: 'Messages array is required',
        code: 'INVALID_REQUEST'
      });
    }

    // Validate Groq API key
    if (!process.env.GROQ_API_KEY) {
      return res.status(500).json({ 
        error: 'Groq API key not configured',
        code: 'API_KEY_MISSING'
      });
    }

    // Clean messages - remove unsupported properties
    const cleanedMessages = messages.map(msg => {
      return {
        role: msg.role,
        content: msg.content
      };
    });

    // Validate message structure
    for (let i = 0; i < cleanedMessages.length; i++) {
      const msg = cleanedMessages[i];
      if (!msg.role || !msg.content) {
        return res.status(400).json({
          error: `Invalid message format at index ${i}. Required: role and content`,
          code: 'INVALID_MESSAGE_FORMAT'
        });
      }
      
      if (!['user', 'assistant', 'system'].includes(msg.role)) {
        return res.status(400).json({
          error: `Invalid role '${msg.role}' at index ${i}. Must be 'user', 'assistant', or 'system'`,
          code: 'INVALID_ROLE'
        });
      }
    }

    console.log('Processing chat request with model:', model);
    console.log('Cleaned messages:', JSON.stringify(cleanedMessages));

    // Call Groq API
    const completion = await groq.chat.completions.create({
      messages: cleanedMessages,
      model: model,
      temperature: 0.7,
      max_tokens: 1024,
      top_p: 1,
      stream: false
    });

    const aiMessage = completion.choices[0].message.content;
    
    console.log('✅ AI Response generated successfully');

    res.json({
      message: aiMessage,
      model: completion.model,
      tokens: completion.usage?.total_tokens || 0,
      id: completion.id,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('❌ Groq API Error:', error);
    
    // Handle specific errors
    if (error.status === 401) {
      return res.status(401).json({ 
        error: 'Invalid Groq API key. Please check your credentials.',
        code: 'INVALID_API_KEY'
      });
    }

    if (error.status === 429) {
      return res.status(429).json({ 
        error: 'API rate limit exceeded. Please try again later.',
        code: 'RATE_LIMIT_EXCEEDED'
      });
    }

    if (error.code === 'ENOTFOUND' || error.code === 'ECONNREFUSED') {
      return res.status(503).json({
        error: 'Service temporarily unavailable. Please try again.',
        code: 'SERVICE_UNAVAILABLE'
      });
    }

    res.status(500).json({ 
      error: 'Failed to process your request',
      details: error.message,
      code: 'INTERNAL_ERROR'
    });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'healthy',
    service: 'Groq Chatbot API',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    groq_configured: !!process.env.GROQ_API_KEY
  });
});

// Get available models
app.get('/api/models', (req, res) => {
  res.json({
    models: [
      { 
        id: 'llama-3.1-8b-instant', 
        name: 'Llama 3.1 8B Instant', 
        description: 'Fastest model, ideal for real-time applications',
        max_tokens: 8192,
        context_window: 8192
      },
      { 
        id: 'llama-3.1-70b-versatile', 
        name: 'Llama 3.1 70B Versatile', 
        description: 'Most capable model for complex tasks',
        max_tokens: 8192,
        context_window: 8192
      },
      { 
        id: 'mixtral-8x7b-32768', 
        name: 'Mixtral 8x7B', 
        description: 'Excellent for coding and complex reasoning',
        max_tokens: 4096,
        context_window: 32768
      },
      { 
        id: 'gemma2-9b-it', 
        name: 'Gemma 2 9B', 
        description: 'Great balance of speed and quality',
        max_tokens: 8192,
        context_window: 8192
      }
    ]
  });
});

// Serve main page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/index.html'));
});

// Serve chatbot.js
app.get('/chatbot.js', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/chatbot.js'));
});

// 404 handler for API routes
app.use('/api/*', (req, res) => {
  res.status(404).json({ 
    error: 'API endpoint not found',
    code: 'NOT_FOUND',
    path: req.originalUrl
  });
});

// Global error handler
app.use((error, req, res, next) => {
  console.error('🚨 Unhandled Error:', error);
  res.status(500).json({
    error: 'Internal server error',
    code: 'INTERNAL_SERVER_ERROR'
  });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Groq Chatbot Server running on http://localhost:${PORT}`);
  console.log(`📡 API Health: http://localhost:${PORT}/api/health`);
  console.log(`💬 Chat API: http://localhost:${PORT}/api/chat`);
  console.log(`🔧 Models API: http://localhost:${PORT}/api/models`);
  console.log(`🌐 Frontend: http://localhost:${PORT}`);
  console.log(`🔑 Groq API Configured: ${!!process.env.GROQ_API_KEY}`);
  
  if (!process.env.GROQ_API_KEY) {
    console.log(`❌ WARNING: GROQ_API_KEY not found in .env file`);
    console.log(`   Get your API key from: https://console.groq.com`);
  }
});