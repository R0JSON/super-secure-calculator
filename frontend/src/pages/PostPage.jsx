import React, { useState, useEffect } from 'react';
import './PostPage.css';
import { sanitizeComment, validateComment } from '../utils/sanitize';

const PostsPage = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [commentInputs, setCommentInputs] = useState({});
  const [submittingComments, setSubmittingComments] = useState({});
  const [commentErrors, setCommentErrors] = useState({});

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/posts/public/');

      if (!response.ok) {
        throw new Error('Failed to fetch posts');
      }

      const data = await response.json();
      setPosts(data.data || []);

      // Fetch comments for each post
      data.data.forEach(post => {
        fetchComments(post.id);
      });
    } catch (err) {
      setError('Error loading posts. Please try again later.');
      console.error('Error fetching posts:', err);
    } finally {
      setLoading(false);
    }
  };

const fetchComments = async (postId) => {
  try {
    const response = await fetch(`/api/v1/comments/post/${postId}`);
    if (response.ok) {
      const data = await response.json();
      console.log('Comments API response for post', postId, ':', data); // Debug

      setPosts(prevPosts =>
        prevPosts.map(post =>
          post.id === postId
            ? { ...post, comments: data.data || [] }
            : post
        )
      );
    }
  } catch (err) {
    console.error('Error fetching comments:', err);
  }
};

const handleCommentChange = (postId, content) => {
    setCommentInputs(prev => ({
      ...prev,
      [postId]: content
    }));

    // Clear error when user starts typing
    if (commentErrors[postId]) {
      setCommentErrors(prev => ({
        ...prev,
        [postId]: ''
      }));
    }
  };

  const submitComment = async (postId) => {
    let content = commentInputs[postId]?.trim();
    if (!content) return;

    // Validate comment
    const validation = validateComment(content);
    if (!validation.isValid) {
      setCommentErrors(prev => ({
        ...prev,
        [postId]: validation.error
      }));
      return;
    }

    // Sanitize comment
    content = sanitizeComment(content);

    const token = localStorage.getItem('accessToken');
    if (!token) {
      alert('Please log in to comment');
      return;
    }

    setSubmittingComments(prev => ({ ...prev, [postId]: true }));
    setCommentErrors(prev => ({ ...prev, [postId]: '' }));

    try {
      const response = await fetch('/api/v1/comments/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          post_id: postId,
          content: content
        })
      });

      if (response.ok) {
        setCommentInputs(prev => ({ ...prev, [postId]: '' }));
        // Refresh comments for this post
        fetchComments(postId);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to post comment');
      }
    } catch (err) {
      setCommentErrors(prev => ({
        ...prev,
        [postId]: err.message || 'Error posting comment. Please try again.'
      }));
      console.error('Error posting comment:', err);
    } finally {
      setSubmittingComments(prev => ({ ...prev, [postId]: false }));
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getOperationSymbol = (operation) => {
    const symbols = {
      add: '+',
      sub: '-',
      mul: '×',
      div: '÷'
    };
    return symbols[operation] || operation;
  };

const getAuthorName = (owner) => {
  console.log('getAuthorName called with:', owner); // Debug

  if (owner && owner.full_name && owner.full_name.trim() !== '') {
    return owner.full_name;
  }

  return 'Community Member';
};



  if (loading) {
    return (
      <div className="posts-page">
        <div className="posts-container">
          <h1>Calculation Posts</h1>
          <div className="loading">Loading posts...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="posts-page">
        <div className="posts-container">
          <h1>Calculation Posts</h1>
          <div className="error-message">{error}</div>
          <button onClick={fetchPosts} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="posts-page">
      <div className="posts-container">
        <h1>Calculation Posts</h1>
        <p className="page-description">
          Discover interesting calculations shared by our community
        </p>

        {posts.length === 0 ? (
          <div className="no-posts">
            <h3>No posts yet</h3>
            <p>Be the first to share a calculation!</p>
          </div>
        ) : (
          <div className="posts-grid">
            {posts.map((post) => (
              <div key={post.id} className="post-card">
                <div className="post-header">
                  <h3 className="post-title">{post.title}</h3>
                  {post.description && (
                    <p className="post-description">{post.description}</p>
                  )}
                </div>

                {post.calculation && (
                  <div className="calculation-display">
                    <div className="calculation-formula">
                      <span className="operand">{post.calculation.operand_a}</span>
                      <span className="operator">
                        {getOperationSymbol(post.calculation.operation)}
                      </span>
                      <span className="operand">{post.calculation.operand_b}</span>
                      <span className="equals">=</span>
                      <span className="result">{post.calculation.result}</span>
                    </div>
                    <div className="calculation-details">
                      <span className="operation-name">
                        {post.calculation.operation.toUpperCase()}
                      </span>
                    </div>
                  </div>
                )}

                {/* Comments Section */}
                <div className="comments-section">
                  <h4 className="comments-title">
                    Comments ({post.comments ? post.comments.length : 0})
                  </h4>

                  {/* Comments List */}
                  {post.comments && post.comments.length > 0 ? (
                  <div className="comments-list">
                    {post.comments.map((comment) => {
                      console.log('Full comment:', comment);
                      console.log('Comment owner:', comment.owner);
                      console.log('Owner full_name:', comment.owner?.full_name);

                      return (
                        <div key={comment.id} className="comment-item">
                          <div className="comment-header">
                            <span className="comment-author">
                              {getAuthorName(comment.owner)}
                            </span>
                            <span className="comment-date">
                              {formatDate(comment.created_at)}
                            </span>
                          </div>
                          <p className="comment-content">{comment.content}</p>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <p className="no-comments">No comments yet. Be the first to comment!</p>
                )}

                  {/* Add Comment Form */}
                  <div className="add-comment">
                    <textarea
                      value={commentInputs[post.id] || ''}
                      onChange={(e) => handleCommentChange(post.id, e.target.value)}
                      placeholder="Add a comment..."
                      rows="3"
                      className={`comment-input ${commentErrors[post.id] ? 'error' : ''}`}
                    />
                    {commentErrors[post.id] && (
                      <div className="comment-error">{commentErrors[post.id]}</div>
                    )}
                    <button
                      onClick={() => submitComment(post.id)}
                      disabled={!commentInputs[post.id]?.trim() || submittingComments[post.id]}
                      className="comment-submit-btn"
                    >
                      {submittingComments[post.id] ? 'Posting...' : 'Post Comment'}
                    </button>
                  </div>
                </div>

                <div className="post-footer">
                  <div className="post-meta">
                    <div className="author-info">
                      <span className="author-name">
                        By {getAuthorName(post.owner)}
                      </span>
                    </div>
                    <span className="post-date">
                      {formatDate(post.created_at)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default PostsPage;