import PropTypes from "prop-types";
import {Button} from "@/components/ui/button";

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
        <Button type="submit">{buttonText}</Button>
    );
};

SubmitButton.propTypes = {
    buttonText: PropTypes.string.isRequired,
};

export default SubmitButton;
