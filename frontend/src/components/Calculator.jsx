import React, { useState, useEffect } from 'react';
import apiClient from '../api/axiosConfig';
import './Calculator.css';

const operationSymbols = {
  add: '+',
  sub: '-',
  mul: '*',
  div: '/',
};

function Calculator() {
  const [history, setHistory] = useState([]);
  const [operandA, setOperandA] = useState('');
  const [operandB, setOperandB] = useState('');
  const [operation, setOperation] = useState('add');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [postingId, setPostingId] = useState(null); // Track which calculation is being posted
  const [showPostModal, setShowPostModal] = useState(false);
  const [currentCalculation, setCurrentCalculation] = useState(null);
  const [postTitle, setPostTitle] = useState('');
  const [postDescription, setPostDescription] = useState('');

  // Fetch initial calculation history when the component mounts
  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await apiClient.get('/calculations/');
      // Sort history to show the most recent calculations first
      setHistory(response.data.data.reverse());
    } catch (err) {
      setError('Could not fetch calculation history.');
      console.error(err);
    }
  };

  const handleCalculate = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setResult(null);

    if (operation === 'div' && parseFloat(operandB) === 0) {
      setError('Error: Division by zero is not allowed.');
      setIsLoading(false);
      return;
    }

    try {
      const payload = {
        operand_a: parseInt(operandA, 10),
        operand_b: parseInt(operandB, 10),
        operation,
      };

      const response = await apiClient.post('/calculations/', payload);

      setResult(response.data.result);
      fetchHistory();
    } catch (err) {
      setError('Calculation failed. Please ensure both operands are valid numbers.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePostCalculation = (calculation) => {
    setCurrentCalculation(calculation);
    // Generate a default title based on the calculation
    setPostTitle(`${calculation.operand_a} ${operationSymbols[calculation.operation]} ${calculation.operand_b} = ${calculation.result}`);
    setPostDescription('');
    setShowPostModal(true);
  };

  const handleCreatePost = async () => {
    if (!postTitle.trim()) {
      setError('Please enter a title for your post.');
      return;
    }

    setPostingId(currentCalculation.id);
    setError('');

    try {
      const postData = {
        title: postTitle,
        description: postDescription,
        calculation_id: currentCalculation.id,
      };

      await apiClient.post('/posts/', postData);

      // Reset and close modal
      setShowPostModal(false);
      setCurrentCalculation(null);
      setPostTitle('');
      setPostDescription('');

      // Show success message
      setError(''); // Clear any previous errors
      alert('Post created successfully!');

    } catch (err) {
      setError('Failed to create post. Please try again.');
      console.error(err);
    } finally {
      setPostingId(null);
    }
  };

  const closeModal = () => {
    setShowPostModal(false);
    setCurrentCalculation(null);
    setPostTitle('');
    setPostDescription('');
    setError('');
  };

  const getCalculationFormula = (calc) => {
    return `${calc.operand_a} ${operationSymbols[calc.operation]} ${calc.operand_b} = ${calc.result}`;
  };

  return (
    <div className="calculator-container">
      <h2>Super Secure Calculator</h2>
      <form onSubmit={handleCalculate} className="calculator-form">
        <input
          type="number"
          value={operandA}
          onChange={(e) => setOperandA(e.target.value)}
          placeholder="Operand A"
          required
          aria-label="Operand A"
        />
        <select
          value={operation}
          onChange={(e) => setOperation(e.target.value)}
          aria-label="Operation"
        >
          <option value="add">+</option>
          <option value="sub">-</option>
          <option value="mul">*</option>
          <option value="div">/</option>
        </select>
        <input
          type="number"
          value={operandB}
          onChange={(e) => setOperandB(e.target.value)}
          placeholder="Operand B"
          required
          aria-label="Operand B"
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Calculating...' : 'Calculate'}
        </button>
      </form>

      {error && !showPostModal && <p className="error-message">{error}</p>}
      {result !== null && (
        <div className="result-display">
          <h3>Result: <span>{result}</span></h3>
        </div>
      )}

      <div className="history-container">
        <h3>Calculation History</h3>
        {history.length > 0 ? (
          <ul>
            {history.map((calc) => (
              <li key={calc.id}>
                <div className="calculation-info">
                  <span className="calculation-formula">
                    {getCalculationFormula(calc)}
                  </span>
                </div>
                <button
                  className="post-button"
                  onClick={() => handlePostCalculation(calc)}
                  disabled={postingId === calc.id}
                >
                  {postingId === calc.id ? 'Posting...' : 'Post'}
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p>No calculations have been performed yet.</p>
        )}
      </div>

      {/* Post Creation Modal */}
      {showPostModal && currentCalculation && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Create Post from Calculation</h3>
              <button className="close-button" onClick={closeModal}>×</button>
            </div>

            <div className="calculation-preview">
              <strong>Calculation:</strong> {getCalculationFormula(currentCalculation)}
            </div>

            <div className="form-group">
              <label htmlFor="post-title">Post Title *</label>
              <input
                id="post-title"
                type="text"
                value={postTitle}
                onChange={(e) => setPostTitle(e.target.value)}
                placeholder="Enter a title for your post"
                maxLength="255"
              />
            </div>

            <div className="form-group">
              <label htmlFor="post-description">Description (Optional)</label>
              <textarea
                id="post-description"
                value={postDescription}
                onChange={(e) => setPostDescription(e.target.value)}
                placeholder="Add a description or context for this calculation..."
                rows="3"
                maxLength="500"
              />
            </div>

            {error && <p className="error-message">{error}</p>}

            <div className="modal-actions">
              <button className="cancel-button" onClick={closeModal}>
                Cancel
              </button>
              <button
                className="create-post-button"
                onClick={handleCreatePost}
                disabled={!postTitle.trim() || postingId}
              >
                {postingId ? 'Creating Post...' : 'Create Post'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Calculator;