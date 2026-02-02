import React from 'react';

interface SymbolMap {
  [key: string]: {
    symbol: string;
    className: string;
  };
}

const OPERATORS: SymbolMap = {
  '^': { symbol: '∧', className: 'symbol-and' },
  '&': { symbol: '∧', className: 'symbol-and' },
  'AND': { symbol: '∧', className: 'symbol-and' },
  'v': { symbol: '∨', className: 'symbol-or' },
  '|': { symbol: '∨', className: 'symbol-or' },
  'OR': { symbol: '∨', className: 'symbol-or' },
  '~': { symbol: '¬', className: 'symbol-not' },
  '!': { symbol: '¬', className: 'symbol-not' },
  'NOT': { symbol: '¬', className: 'symbol-not' },
  '->': { symbol: '→', className: 'symbol-implies' },
  '=>': { symbol: '→', className: 'symbol-implies' },
  'IMPLIES': { symbol: '→', className: 'symbol-implies' },
  '__invert__': { symbol: '¬', className: 'symbol-not' },
  '__add__': { symbol: '∨', className: 'symbol-or' },
  '__mul__': { symbol: '∧', className: 'symbol-and' },
  '__rshift__': { symbol: '→', className: 'symbol-implies' },
};

const CONSTANTS: SymbolMap = {
  'T': { symbol: '⊤', className: 'symbol-true' },
  'F': { symbol: '⊥', className: 'symbol-false' },
  'True': { symbol: '⊤', className: 'symbol-true' },
  'False': { symbol: '⊥', className: 'symbol-false' },
};

export function renderProposition(text: string): React.ReactNode {
  if (!text) return null;

  const elements: React.ReactNode[] = [];
  let i = 0;
  let key = 0;

  while (i < text.length) {
    const char = text[i];

    // Check for multi-character operators
    if (text.substring(i, i + 2) === '->') {
      elements.push(
        <span key={key++} className="proposition-symbol symbol-implies"> → </span>
      );
      i += 2;
      continue;
    }
    if (text.substring(i, i + 2) === '=>') {
      elements.push(
        <span key={key++} className="proposition-symbol symbol-implies"> → </span>
      );
      i += 2;
      continue;
    }

    // Check for operator names
    for (const [op, { symbol, className }] of Object.entries(OPERATORS)) {
      if (text.substring(i, i + op.length).toUpperCase() === op.toUpperCase() && op.length > 1) {
        elements.push(
          <span key={key++} className={`proposition-symbol ${className}`}> {symbol} </span>
        );
        i += op.length;
        continue;
      }
    }

    // Single character operators
    if (OPERATORS[char]) {
      const { symbol, className } = OPERATORS[char];
      elements.push(
        <span key={key++} className={`proposition-symbol ${className}`}>
          {char === '~' || char === '!' ? symbol : ` ${symbol} `}
        </span>
      );
      i++;
      continue;
    }

    // Constants
    if (CONSTANTS[char]) {
      const { symbol, className } = CONSTANTS[char];
      elements.push(
        <span key={key++} className={`proposition-symbol ${className}`}>{symbol}</span>
      );
      i++;
      continue;
    }

    // Parentheses
    if (char === '(' || char === ')') {
      elements.push(
        <span key={key++} className="proposition-symbol symbol-paren">{char}</span>
      );
      i++;
      continue;
    }

    // Variables (letters)
    if (/[a-zA-Z]/.test(char)) {
      let variable = '';
      while (i < text.length && /[a-zA-Z0-9]/.test(text[i])) {
        variable += text[i];
        i++;
      }

      // Check if it's a constant
      if (CONSTANTS[variable]) {
        const { symbol, className } = CONSTANTS[variable];
        elements.push(
          <span key={key++} className={`proposition-symbol ${className}`}>{symbol}</span>
        );
      } else if (OPERATORS[variable.toUpperCase()]) {
        const { symbol, className } = OPERATORS[variable.toUpperCase()];
        elements.push(
          <span key={key++} className={`proposition-symbol ${className}`}> {symbol} </span>
        );
      } else {
        elements.push(
          <span key={key++} className="proposition-symbol symbol-var" style={{ fontStyle: 'italic' }}>
            {variable}
          </span>
        );
      }
      continue;
    }

    // Whitespace and other characters
    if (char === ' ') {
      i++;
      continue;
    }

    elements.push(<span key={key++}>{char}</span>);
    i++;
  }

  return <span className="proposition-rendered">{elements}</span>;
}

export function PropositionDisplay({
  text,
  size = 'medium',
  showOriginal = false
}: {
  text: string;
  size?: 'small' | 'medium' | 'large';
  showOriginal?: boolean;
}) {
  const fontSize = {
    small: '0.9rem',
    medium: '1.1rem',
    large: '1.4rem',
  }[size];

  return (
    <span style={{ fontSize, fontFamily: '"Cambria Math", "Times New Roman", serif' }}>
      {renderProposition(text)}
      {showOriginal && (
        <span style={{ fontSize: '0.75em', color: '#64748b', marginTop: '4px', display: 'block' }}>
          {text}
        </span>
      )}
    </span>
  );
}

export default renderProposition;
