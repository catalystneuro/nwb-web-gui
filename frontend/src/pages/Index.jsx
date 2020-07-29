import React, { useEffect, useState, useMemo } from 'react';
import { Row, Col, Container, Accordion, Card, Button } from 'react-bootstrap'
import { Styles } from '../styles/index'
import Form from "@rjsf/core";
import { siteContent } from '../api/index'


const Index = () => {

    const defaultSchema = [{
        title: "My form",
    }];
    const [nwbSchema, setSchema] = useState(defaultSchema);

    useEffect(() => {
        fetch("/index")
            .then((res) => res.json())
            .then((data) => {
                setSchema(data.data);

            });
    }, []);

    const nwbForm = useMemo(() => {
        return (
            nwbSchema.map((nwb, index) => {
                return (
                    /*
                    < Card >
                        <Card.Header>
                            <Accordion.Toggle as={Button} variant="link" eventKey={index}>
                                Form {index}
                            </Accordion.Toggle>
                        </Card.Header>
                        <Accordion.Collapse eventKey={index}>
                            <Card.Body>
                                <Form key={nwb} schema={nwb} />
                            </Card.Body>
                        </Accordion.Collapse>
                    </Card >
                    */
                    <Form schema={nwb} />
                )
            })
        )
    }, [nwbSchema])



    return (
        <Styles>
            <Container fluid>
                <Row>
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