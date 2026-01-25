import { ButtonHTMLAttributes, forwardRef } from 'react';
import clsx from 'clsx';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'outline' | 'ghost' | 'danger';
    size?: 'sm' | 'md' | 'lg';
    isLoading?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(({
    className,
    variant = 'primary',
    size = 'md',
    isLoading,
    children,
    disabled,
    ...props
}, ref) => {
    return (
        <button
            ref={ref}
            className={clsx(
                'btn',
                'inline-flex items-center justify-center rounded transition-colors disabled:opacity-50 disabled:pointer-events-none',
                {
                    'bg-[var(--color-yellow)] text-[var(--color-black)] hover:brightness-95': variant === 'primary',
                    'border-2 border-[var(--color-black)] bg-transparent hover:bg-[var(--color-black)] hover:text-[var(--color-yellow)]': variant === 'outline',
                    'hover:bg-gray-100': variant === 'ghost',
                    'bg-[var(--color-red)] text-white hover:brightness-90': variant === 'danger',
                    'h-8 px-3 text-sm': size === 'sm',
                    'h-10 px-4': size === 'md',
                    'h-12 px-6 text-lg': size === 'lg',
                },
                className
            )}
            disabled={disabled || isLoading}
            {...props}
        >
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {children}
        </button>
    );
});

Button.displayName = 'Button';

export { Button };
