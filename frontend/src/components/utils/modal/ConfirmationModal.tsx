import './ConfirmationModal.css';

/**
* ConfirmationModal component for displaying a confirmation dialog.
*
* Props:
* - isOpen: boolean to control visibility of the modal
* - title: string for the modal title
* - message: string for the confirmation message
* - onConfirm: function to call when the user confirms the action
* - onCancel: function to call when the user cancels the action
*/
interface Props {
    isOpen: boolean;
    title: string;
    message: string;
    onConfirm: () => void;
    onCancel: () => void;
}

/**
* Displays a modal dialog with a title, message, and two buttons for confirmation and cancellation.
* If `isOpen` is false, the modal will not be rendered.
*/
const ConfirmationModal = ({ isOpen, title, message, onConfirm, onCancel }: Props) => {
    if (!isOpen) return null;

    return (
        <div className="modal-overlay">
            <div className="confirmation-modal">
                <div className="confirmation-header">
                    <h2>{title}</h2>
                </div>
                <div className="confirmation-body">
                    <p>{message}</p>
                </div>
                <div className="confirmation-footer">
                    <button className="cancel-button" onClick={onCancel}>
                        Cancel
                    </button>
                    <button className="confirm-button" onClick={onConfirm}>
                        Delete
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ConfirmationModal;
