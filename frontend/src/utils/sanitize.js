/**
 * Sanitize comment content before submission
 * Only do minimal sanitization in frontend, let backend handle the main sanitization
 */
export const sanitizeComment = (content) => {
  if (!content) return content;

  console.log('Frontend sanitization input:', content);

  // Only trim whitespace in frontend
  // Don't do HTML escaping here - let backend handle it once
  let sanitized = content.trim();

  // Remove excessive whitespace (optional)
  sanitized = sanitized.replace(/\s+/g, ' ');

  console.log('Frontend sanitization output:', sanitized);
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