import React from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "danger" | "ghost";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  className,
  variant = "primary",
  size = "md",
  isLoading = false,
  icon,
  disabled,
  ...props
}) => {
  const baseStyles =
    "touch-target inline-flex items-center justify-center font-medium rounded-lg transition-colors focus-visible:ring-2 disabled:opacity-50 disabled:cursor-not-allowed select-none";

  const variants = {
    primary: "bg-[#1E3A2B] text-white hover:bg-[#284D3A] active:bg-[#14291E] shadow-sm",
    secondary: "bg-[#E8F0EC] text-[#1E3A2B] hover:bg-[#D5E5DC] active:bg-[#C2D9CD]",
    outline: "border-2 border-[#1E3A2B] text-[#1E3A2B] bg-transparent hover:bg-[#E8F0EC]",
    danger: "bg-[#C92A2A] text-white hover:bg-[#A61E1E] active:bg-[#861818]",
    ghost: "bg-transparent text-[#1A241F] hover:bg-[#E5E0D8]",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-sm gap-1.5",
    md: "px-4 py-2.5 text-base gap-2",
    lg: "px-6 py-3.5 text-lg gap-2.5",
  };

  return (
    <button
      className={twMerge(clsx(baseStyles, variants[variant], sizes[size], className))}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-2" />
      ) : icon ? (
        <span className="shrink-0">{icon}</span>
      ) : null}
      {children}
    </button>
  );
};
