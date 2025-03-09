import React from "react";

const Button = ({ isActive, onClick, children }) => {
  return (
    <button
      onClick={isActive ? onClick : null}
      className={`px-4 py-2 rounded-md text-white font-semibold ${
        isActive
          ? "bg-blue-500 hover:bg-blue-600 cursor-pointer"
          : "bg-gray-300 cursor-not-allowed"
      }`}
      disabled={!isActive}
    >
      {children}
    </button>
  );
};

export default Button;
