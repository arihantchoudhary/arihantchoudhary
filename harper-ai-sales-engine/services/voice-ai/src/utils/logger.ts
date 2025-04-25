import winston from 'winston';
import config from 'config';

// Get logging configuration from config
const logConfig = config.get('logging') as { level: string; format: string };

// Create logger instance
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || logConfig.level || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    logConfig.format === 'json' 
      ? winston.format.json() 
      : winston.format.simple()
  ),
  defaultMeta: { service: 'voice-ai-service' },
  transports: [
    // Console transport for development
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    // File transport for production
    new winston.transports.File({ 
      filename: 'logs/error.log', 
      level: 'error',
      dirname: process.env.LOG_DIR || './logs',
      maxsize: 10485760, // 10MB
      maxFiles: 5,
    }),
    new winston.transports.File({ 
      filename: 'logs/combined.log',
      dirname: process.env.LOG_DIR || './logs',
      maxsize: 10485760, // 10MB
      maxFiles: 5,
    })
  ]
});

// If we're not in production, add pretty console output
if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.combine(
      winston.format.colorize(),
      winston.format.simple()
    )
  }));
}

export { logger };
