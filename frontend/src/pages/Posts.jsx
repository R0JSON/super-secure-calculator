                     import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import api from '../api/axiosConfig';
import './Posts.css';

const Posts = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useOutletContext();

  useEffect(() => {
    fetchUserPosts();
  }, []);

  const fetchUserPosts = async () => {
    try {
      setLoading(true);
      const response = await api.get('/posts/');
      setPosts(response.data.data || []);
    } catch (err) {
      setError('Failed to load posts');
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
    });
  };

  if (loading) {
    return (
      <div className="posts-container">
        <h1>My Posts</h1>
        <div className="loading">Loading your posts...</div>
      </div>
    );
  }

  return (
    <div className="posts-container">
      <h1>My Posts</h1>

      {error && <div className="error-message">{error}</div>}

      {posts.length === 0 ? (
        <div className="no-posts">
          <h3>No posts yet</h3>
          <p>Create your first post by sharing a calculation from the calculator!</p>
        </div>
      ) : (
        <div className="posts-list">
          {posts.map((post) => (
            <div key={post.id} className="post-item">
              <h3>{post.title}</h3>
              {post.description && (
                <p className="post-description">{post.description}</p>
              )}
              {post.calculation && (
                <div className="calculation-preview">
                  <strong>Calculation:</strong> {post.calculation.operand_a} {post.calculation.operation} {post.calculation.operand_b} = {post.calculation.result}
                </div>
              )}
              <div className="post-meta">
                <span className="post-date">
                  Created: {formatDate(post.created_at)}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Posts;
