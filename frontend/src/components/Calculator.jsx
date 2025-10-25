import React, { useState, useEffect } from 'react';
import apiClient from '../api/axiosConfig';
import './Calculator.css'; // We will create this file for styling

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
    e.preventDefault(); // Prevent form submission from reloading the page
    setIsLoading(true);
    setError('');
    setResult(null);

    // Basic validation
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
      // After a successful calculation, refresh the history list
      fetchHistory();
    } catch (err) {
      setError('Calculation failed. Please ensure both operands are valid numbers.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
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

      {error && <p className="error-message">{error}</p>}
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
                {calc.operand_a} {operationSymbols[calc.operation]} {calc.operand_b} = <strong>{calc.result}</strong>
              </li>
            ))}
          </ul>
        ) : (
          <p>No calculations have been performed yet.</p>
        )}
      </div>
    </div>
  );
}

export default Calculator;