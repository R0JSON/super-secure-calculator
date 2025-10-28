/**
 * Sanitize user input to prevent XSS attacks
 */
export const sanitizeInput = (input) => {
  if (typeof input !== 'string') return input;

  const div = document.createElement('div');
  div.textContent = input;
  return div.innerHTML;
};

/**
 * Sanitize comment content before submission
 */
export const sanitizeComment = (content) => {
  if (!content) return content;

  // Trim whitespace
  let sanitized = content.trim();

  // Remove potentially dangerous content
  const dangerousPatterns = [
    /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
    /on\w+\s*=/gi,
    /javascript:/gi,
    /vbscript:/gi,
    /expression\s*\(/gi,
    /url\s*\(/gi,
  ];

  dangerousPatterns.forEach(pattern => {
    sanitized = sanitized.replace(pattern, '');
  });

  // Limit consecutive spaces
  sanitized = sanitized.replace(/ {2,}/g, ' ');

  // Limit consecutive newlines
  sanitized = sanitized.replace(/\n{3,}/g, '\n\n');

  return sanitized;
};

/**
 * Validate comment content
 */
export const validateComment = (content) => {
  if (!content || content.trim().length === 0) {
    return { isValid: false, error: 'Comment cannot be empty' };
  }

  if (content.length > 1000) {
    return { isValid: false, error: 'Comment cannot exceed 1000 characters' };
  }

  // Check for only whitespace
  if (content.trim().length === 0) {
    return { isValid: false, error: 'Comment cannot be only whitespace' };
  }

  return { isValid: true, error: null };
};