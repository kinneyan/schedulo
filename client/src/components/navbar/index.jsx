import Container from 'react-bootstrap/Container';
import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';

import './index.scss';

const NavigationBar = () => {
    return (
        <Navbar fixed="top">
            <Container fluid className="p-0">
                <Navbar.Brand href="#">
                    <img 
                        src='/schedulo.png'
                        alt='logo'
                    />
                    {' '}Schedulo
                </Navbar.Brand>
                <Nav id="page-links">
                    <Nav.Link href="/">Home</Nav.Link>
                    <Nav.Link href="#">About</Nav.Link>
                    <Nav.Link href="/login">Log in</Nav.Link>
                </Nav>
            </Container>
        </Navbar>
    );
};

export default NavigationBar;
