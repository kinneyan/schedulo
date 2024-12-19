import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';

import './index.scss';

const SubmitButton = ({ button_text }) => {
    return (
        <Button id="button-item">{button_text}</Button>
    );
};

export default SubmitButton;
