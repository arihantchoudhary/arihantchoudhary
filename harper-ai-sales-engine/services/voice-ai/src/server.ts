import express from 'express';
import http from 'http';
import { Server as SocketIOServer } from 'socket.io';
import cors from 'cors';
import config from 'config';
import { logger } from './utils/logger';
import routes from './routes';

// Initialize express app
const app = express();
const server = http.createServer(app);
const io = new SocketIOServer(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  }
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Load service configuration
const serviceConfig = config.get('services.voice_ai');
const port = process.env.PORT || serviceConfig.port || 3001;
const host = serviceConfig.host || '0.0.0.0';

// Routes
app.use('/api', routes);

// Websocket handling for real-time voice AI communications
io.on('connection', (socket) => {
  logger.info(`Client connected: ${socket.id}`);

  // Handle incoming voice stream
  socket.on('voiceStream', (audioData) => {
    // Process the audio data and generate AI response
    // This is where we'll implement the voice AI logic
    // For now, we'll just echo the event for testing
    socket.emit('aiResponse', { message: 'Voice data received' });
  });

  socket.on('disconnect', () => {
    logger.info(`Client disconnected: ${socket.id}`);
  });
});

// Start server
server.listen(port, host as string, () => {
  logger.info(`Voice AI service running at http://${host}:${port}`);
  logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.error('Uncaught exception', { error: error.message, stack: error.stack });
  process.exit(1);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled rejection', { reason, promise });
  process.exit(1);
});

export { app, server, io };
