import { InputHTMLAttributes, LabelHTMLAttributes, TextareaHTMLAttributes, forwardRef } from "react";

export const Label = ({ className = "", ...props }: LabelHTMLAttributes<HTMLLabelElement>) => (
  <label className={`mb-1.5 block text-sm font-medium text-mist ${className}`} {...props} />
);

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  ({ className = "", ...props }, ref) => (
    <input
      ref={ref}
      className={`w-full rounded-lg border border-ink-border bg-ink px-3.5 py-2.5 text-sm text-paper placeholder:text-mist-dim focus:border-gold/60 focus:outline-none focus:ring-1 focus:ring-gold/40 ${className}`}
      {...props}
    />
  )
);
Input.displayName = "Input";

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaHTMLAttributes<HTMLTextAreaElement>>(
  ({ className = "", ...props }, ref) => (
    <textarea
      ref={ref}
      className={`w-full rounded-lg border border-ink-border bg-ink px-3.5 py-2.5 text-sm text-paper placeholder:text-mist-dim focus:border-gold/60 focus:outline-none focus:ring-1 focus:ring-gold/40 ${className}`}
      {...props}
    />
  )
);
Textarea.displayName = "Textarea";
