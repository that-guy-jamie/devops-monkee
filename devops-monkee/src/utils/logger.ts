import chalk from 'chalk';

export enum LogLevel {
  ERROR = 0,
  WARN = 1,
  INFO = 2,
  DEBUG = 3,
  SUCCESS = 4
}

export class Logger {
  private level: LogLevel = LogLevel.INFO;
  private useColors: boolean = true;

  setLevel(level: LogLevel): void {
    this.level = level;
  }

  setColors(useColors: boolean): void {
    this.useColors = useColors;
  }

  error(message: string, ...args: any[]): void {
    this.log(LogLevel.ERROR, message, args);
  }

  warn(message: string, ...args: any[]): void {
    this.log(LogLevel.WARN, message, args);
  }

  info(message: string, ...args: any[]): void {
    this.log(LogLevel.INFO, message, args);
  }

  debug(message: string, ...args: any[]): void {
    this.log(LogLevel.DEBUG, message, args);
  }

  success(message: string, ...args: any[]): void {
    this.log(LogLevel.SUCCESS, message, args);
  }

  private log(level: LogLevel, message: string, args: any[]): void {
    if (level > this.level) {
      return;
    }

    const timestamp = new Date().toISOString();
    const levelName = LogLevel[level];
    const coloredMessage = this.colorize(level, `[${timestamp}] ${levelName}: ${message}`);

    console.log(coloredMessage, ...args);
  }

  private colorize(level: LogLevel, message: string): string {
    if (!this.useColors) {
      return message;
    }

    switch (level) {
      case LogLevel.ERROR:
        return chalk.red(message);
      case LogLevel.WARN:
        return chalk.yellow(message);
      case LogLevel.SUCCESS:
        return chalk.green(message);
      case LogLevel.INFO:
        return chalk.blue(message);
      case LogLevel.DEBUG:
        return chalk.gray(message);
      default:
        return message;
    }
  }

  // Progress logging methods
  startProgress(task: string): ProgressLogger {
    return new ProgressLogger(task, this);
  }

  // Structured logging for governance operations
  logValidationResult(result: {
    score: number;
    grade: string;
    issueCount: number;
    duration: number;
  }): void {
    this.info(`Validation completed in ${result.duration}ms`);
    this.info(`Score: ${result.score}/100 (Grade: ${result.grade})`);
    this.info(`Issues found: ${result.issueCount}`);
  }

  logSyncResult(result: {
    updated: number;
    skipped: number;
    conflicts: number;
    duration: number;
  }): void {
    this.info(`Version sync completed in ${result.duration}ms`);
    this.info(`Files updated: ${result.updated}`);
    this.info(`Files skipped: ${result.skipped}`);
    if (result.conflicts > 0) {
      this.warn(`Conflicts found: ${result.conflicts}`);
    }
  }

  logAuditResult(result: {
    type: string;
    score: number;
    categories: number;
    issues: number;
    duration: number;
  }): void {
    this.info(`${result.type} audit completed in ${result.duration}ms`);
    this.info(`Overall score: ${result.score}/100`);
    this.info(`Categories audited: ${result.categories}`);
    this.info(`Issues identified: ${result.issues}`);
  }
}

export class ProgressLogger {
  private startTime: number;
  private lastUpdate: number;
  private task: string;
  private logger: Logger;

  constructor(task: string, logger: Logger) {
    this.task = task;
    this.logger = logger;
    this.startTime = Date.now();
    this.lastUpdate = this.startTime;
    this.logger.info(`Started: ${task}`);
  }

  update(message: string): void {
    const now = Date.now();
    const elapsed = now - this.lastUpdate;
    this.lastUpdate = now;
    this.logger.debug(`${this.task}: ${message} (+${elapsed}ms)`);
  }

  complete(message?: string): void {
    const totalTime = Date.now() - this.startTime;
    const completionMsg = message || 'completed';
    this.logger.success(`${this.task} ${completionMsg} (${totalTime}ms total)`);
  }

  fail(error: string): void {
    const totalTime = Date.now() - this.startTime;
    this.logger.error(`${this.task} failed: ${error} (${totalTime}ms total)`);
  }
}

// Export singleton instance
export const logger = new Logger();

// Configure based on environment
if (process.env.NODE_ENV === 'production') {
  logger.setLevel(LogLevel.INFO);
} else if (process.env.DEBUG === 'true') {
  logger.setLevel(LogLevel.DEBUG);
}

if (process.env.NO_COLOR === 'true') {
  logger.setColors(false);
}
