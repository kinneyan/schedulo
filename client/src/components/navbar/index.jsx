import Container from 'react-bootstrap/Container';
import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import Cookies from 'universal-cookie';

import './index.scss';

const log_out = () => {
    const cookies = new Cookies();
    cookies.remove('token');
};

const AuthButton = ({ logged_in }) => {
    if (!logged_in)
    {
        return <Nav.Link href="/login">Log in</Nav.Link>;
    }
    return <Nav.Link href="/" onClick={log_out()} >Log out</Nav.Link>;
};

const NavigationBar = ({ logged_in }) => {
    return (
        <Navbar fixed="top">
            <Container fluid className="p-0">
                <Navbar.Brand href="/">
                    <img 
                        src='/schedulo.png'
                        alt='logo'
                    />
                    {' '}Schedulo
                </Navbar.Brand>
                <Nav id="page-links">
                    <Nav.Link href="/">Home</Nav.Link>
                    <Nav.Link href="#">About</Nav.Link>
                    <AuthButton logged_in={logged_in} />
                </Nav>
            </Container>
        </Navbar>
    );
};

export default NavigationBar;
