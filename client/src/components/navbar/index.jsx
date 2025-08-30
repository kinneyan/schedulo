import Container from "react-bootstrap/Container";
import Navbar from "react-bootstrap/Navbar";
import Nav from "react-bootstrap/Nav";
import NavDropdown from "react-bootstrap/NavDropdown";
import Cookies from "universal-cookie";
import PropTypes from "prop-types";

import "./index.scss";

const NavigationBar = ({loggedIn}) => 
{
    const AuthButton = ({loggedIn}) => 
    {
        const logOut = () => 
        {
            const cookies = new Cookies();
            cookies.remove("token");
        };

        if (!loggedIn) 
        {
            return <NavDropdown.Item href="/login">Log in</NavDropdown.Item>;
        }

        return (
            <div>
                <NavDropdown.Item href="/dashboard">Dashboard</NavDropdown.Item>
                <NavDropdown.Item href="/profile">Settings</NavDropdown.Item>
                <NavDropdown.Item href="/" onClick={logOut}>Log out</NavDropdown.Item>
            </div>
        );
    };

    AuthButton.propTypes = {
        loggedIn: PropTypes.bool.isRequired,
    };

    return (
        <Navbar fixed="top">
            <Container fluid className="p-0">
                <Navbar.Brand href="/">
                    <img 
                        src="/schedulo.png"
                        alt="logo"
                    />
                    {" "}Schedulo
                </Navbar.Brand>
                <Nav id="page-links">
                    <Nav.Link href="/">Home</Nav.Link>
                    <Nav.Link href="#">About</Nav.Link>
                    <NavDropdown title="Account">
                        <AuthButton loggedIn={loggedIn} />    
                    </NavDropdown>
                </Nav>
            </Container>
        </Navbar>
    );
};

NavigationBar.propTypes = {
    loggedIn: PropTypes.bool.isRequired,
};

export default NavigationBar;
