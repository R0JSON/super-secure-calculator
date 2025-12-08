import React, { useState, useEffect } from 'react';
import './PostPage.css';
import { sanitizeComment, validateComment } from '../utils/sanitize';
import api from '../api/axiosConfig';

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
      setError('');

      // CORRECT: Axios returns response with data property
      const response = await api.get('/posts/public/');

      // CORRECT: Access data from response.data
      const postsData = response.data.data || [];
      console.log('Fetched posts:', postsData); // Debug
      setPosts(postsData);

      // Fetch comments for each post
      postsData.forEach(post => {
        fetchComments(post.id);
      });
    } catch (err) {
      console.error('Error fetching posts:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Error loading posts. Please try again later.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const fetchComments = async (postId) => {
    try {
      console.log('Fetching comments for post:', postId); // Debug
      const response = await api.get(`/comments/post/${postId}`);

      // CORRECT: Axios response data is in response.data
      const commentsData = response.data.data || [];
      console.log('Comments for post', postId, ':', commentsData);

      setPosts(prevPosts =>
        prevPosts.map(post =>
          post.id === postId
            ? { ...post, comments: commentsData }
            : post
        )
      );
    } catch (err) {
      console.error('Error fetching comments for post', postId, ':', err);
      // Don't set error state for comments to avoid breaking the UI
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
      // CORRECT: Use axios.post() for POST requests
      console.log('Submitting comment for post:', postId, 'Content:', content);
      const response = await api.post('/comments/', {
        post_id: postId,
        content: content
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      console.log('Comment submitted successfully:', response.data);

      // Clear input and refresh comments
      setCommentInputs(prev => ({ ...prev, [postId]: '' }));
      await fetchComments(postId); // Refresh comments for this post

    } catch (err) {
      console.error('Error posting comment:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Error posting comment. Please try again.';
      setCommentErrors(prev => ({
        ...prev,
        [postId]: errorMessage
      }));
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
    console.log('Owner data:', owner); // Debug
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

                {/* Display calculation if available */}
                {post.calculation_id && (
                  <div className="calculation-display">
                    <p>Calculation ID: {post.calculation_id}</p>
                    {/* You might want to fetch calculation details separately */}
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
                      {post.comments.map((comment) => (
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
                      ))}
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