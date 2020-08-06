import React, { useEffect, useState, useMemo } from 'react';
import { Row, Col, Container, Accordion, Card, Button } from 'react-bootstrap'
import { Styles } from '../styles/index'
import Form from "@rjsf/core";
import { siteContent } from '../api/index'
import NavigationBar from "../components/Navbar"
import { toast, ToastContainer } from "react-toastify";
import 'react-toastify/dist/ReactToastify.css';


const Index = () => {

    const defaultSchema = [{
        "Myform": {
            "title": 'My form'
        }
    }];
    const [nwbSchema, setSchema] = useState(defaultSchema);

    useEffect(() => {
        fetch("/index")
            .then((res) => res.json())
            .then((data) => {
                setSchema(data.data);
            });
    }, []);

    const onSubmit = async (e) => {
        const formTitle = e.schema.title
        const formData = e.formData

        const payload = {
            formTitle,
            formData
        };
        const res = await siteContent.sendForm(payload)

        if (res.ok) {
            toast.success('Data Sent!');
        } else {
            toast.error("Something went wrong.");
        }

    }

    // Map forms on data change and return html element with form data
    const nwbForm = useMemo(() => {
        return (
            nwbSchema.map((nwb, index) => {
                return (
                    < Card >
                        <Card.Header>
                            <Accordion.Toggle as={Button} variant="link" eventKey={index + 1}>
                                {Object.keys(nwb)[0]}
                            </Accordion.Toggle>
                        </Card.Header>
                        <Accordion.Collapse eventKey={index + 1}>
                            <Card.Body>
                                <Form key={nwb} schema={Object.values(nwb)[0]} onSubmit={onSubmit} />
                            </Card.Body>
                        </Accordion.Collapse>
                    </Card >
                )
            })
        )
    }, [nwbSchema])


    return (
        <Styles>
            <NavigationBar />
            <Container fluid>
                <Row>
                    <ToastContainer />
                    <Col md={{ span: 10, offset: 1 }}>
                        <Accordion>
                            {nwbForm}
                        </Accordion>
                    </Col>
                </Row>
            </Container>
        </Styles >
    )
}

export default Index;