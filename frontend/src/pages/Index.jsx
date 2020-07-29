import React, { useEffect, useState } from 'react';
import { Row, Col, Container } from 'react-bootstrap'
import { Styles } from '../styles/index'
import Form from "@rjsf/core";


const Index = () => {

    const defaultSchema = {
        title: "My form",
    };
    const [nwbSchema, setSchema] = useState(defaultSchema);

    useEffect(() => {
        fetch("/index")
            .then((res) => res.json())
            .then((data) => {
                setSchema(data.data);
            });
    }, []);

    return (
        <Styles>
            <Container fluid>
                <Row>
                    <Col md={{ span: 10, offset: 1 }}>
                        <Form schema={nwbSchema}></Form>
                    </Col>
                </Row>
            </Container>
        </Styles >
    )
}

export default Index;