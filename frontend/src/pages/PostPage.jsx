import React, { useState, useEffect } from 'react';
import './PostPage.css';

const PostsPage = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

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
    } catch (err) {
      setError('Error loading posts. Please try again later.');
      console.error('Error fetching posts:', err);
    } finally {
      setLoading(false);
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

                <div className="post-footer">
                  <div className="post-meta">
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