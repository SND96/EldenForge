import React from 'react';

const Button = ({ children, variant = 'default', className = '', ...props }) => {
  const baseStyles = 'px-4 py-2 rounded font-medium focus:outline-none focus:ring-2 focus:ring-offset-2';
  const variantStyles = {
    default: 'bg-gray-800 text-white hover:bg-gray-700 focus:ring-gray-500',
    destructive: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
  };

  return (
    <button
      className={`${baseStyles} ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};

export { Button };