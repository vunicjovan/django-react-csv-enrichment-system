import { ReactNode } from 'react';
import './Tooltip.css';

interface Props {
    content: string;
    children: ReactNode;
}

/**
* Tooltip component to display additional information on hover.
*
* @param {string} content - The text to display in the tooltip.
* @param {ReactNode} children - The element that triggers the tooltip on hover.
*/
const Tooltip = ({ content, children }: Props) => {
    return (
        <div className="tooltip-container">
            {children}
            <span className="tooltip-text">{content}</span>
        </div>
    );
};

export default Tooltip;
