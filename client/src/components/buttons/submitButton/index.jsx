import Button from "react-bootstrap/Button";
import PropTypes from "prop-types";

import "./index.scss";

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
