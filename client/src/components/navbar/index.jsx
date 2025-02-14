import Container from 'react-bootstrap/Container';
import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import NavDropdown from 'react-bootstrap/NavDropdown';
import Cookies from 'universal-cookie';

import './index.scss';

const NavigationBar = ({ logged_in }) => 
{
    const AuthButton = ({ logged_in }) => {
        const log_out = () => 
        {
            const cookies = new Cookies();
            cookies.remove('token');
        };
    
        if (!logged_in)
        {
            return <NavDropdown.Item href="/login">Log in</NavDropdown.Item>;
        }
    
        return (
            <div>
                <NavDropdown.Item href='/dashboard'>Dashboard</NavDropdown.Item>
                <NavDropdown.Item href="/profile">Settings</NavDropdown.Item>
                <NavDropdown.Item href="/" onClick={log_out}>Log out</NavDropdown.Item>
            </div>
        );
    };
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
                    <NavDropdown title="Account">
                        <AuthButton logged_in={logged_in} />    
                    </NavDropdown>
                </Nav>
            </Container>
        </Navbar>
    );
};

export default NavigationBar;
