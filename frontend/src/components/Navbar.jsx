import React from "react";
import { Nav, Navbar, Row, Col, Container } from "react-bootstrap";
import { Link, useLocation } from "react-router-dom";
import { Styles } from '../styles/navbar'


const NavigationBar = () => {

    return (
        <Styles>
            <Navbar expand="md" bg="dark" variant="dark">
                <Link to="/index">
                    <Navbar.Brand>
                        NWB-Web-GUI
                        </Navbar.Brand>
                </Link>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav ml-auto">
                    <Nav className="ml-auto">
                        <Nav.Link>
                            <Link className='link' to="/index">Metadata/Conversion </Link>
                        </Nav.Link>
                        <Nav.Link href='http://localhost:5000/explorer'>
                            <a className='link'>NWB Explorer</a>
                        </Nav.Link>
                        <Nav.Link>
                            <Link className='link' to="/custom_dashboards" >Custom Dashboards </Link>
                        </Nav.Link>
                    </Nav>
                </Navbar.Collapse>
            </Navbar>
        </Styles>
    );
};
export default NavigationBar;