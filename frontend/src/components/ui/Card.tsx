import { HTMLAttributes, forwardRef } from 'react';
import clsx from 'clsx';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
    variant?: 'default' | 'paper';
}

const Card = forwardRef<HTMLDivElement, CardProps>(({
    className,
    variant = 'default',
    children,
    ...props
}, ref) => {
    return (
        <div
            ref={ref}
            className={clsx(
                'overflow-hidden transition-all duration-300',
                {
                    'bg-white border border-gray-200 shadow-sm rounded-sm': variant === 'default',
                    'bg-[var(--color-off-white)] border border-[var(--color-black)] shadow-[var(--shadow-sm)] rounded-[var(--border-radius)]': variant === 'paper',
                },
                className
            )}
            {...props}
        >
            {children}
        </div>
    );
});

Card.displayName = 'Card';

export { Card };
