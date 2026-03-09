import Button from "react-bootstrap/Button";
import PropTypes from "prop-types";

import "./index.scss";

/**
 * Submit button for enclosing forms.
 *
 * @param {Object} props
 * @param {string} props.buttonText - Label displayed on the button.
 * @returns {JSX.Element}
 */
const SubmitButton = ({buttonText}) =>
{
    return (
        <Button id="button-item" type="submit">{buttonText}</Button>
    );
};

SubmitButton.propTypes = {
    buttonText: PropTypes.string.isRequired,
};

export default SubmitButton;
