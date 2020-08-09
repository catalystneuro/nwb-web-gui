import React, { useEffect, useState, useMemo, useRef } from 'react';
import { Row, Col, Container, Accordion, Card, Button } from 'react-bootstrap'
import { Form as FormReact } from 'react-bootstrap'
import { Styles } from '../styles/index'
import Form from "@rjsf/core";
import { siteContent } from '../api/index'
import { toast, ToastContainer } from "react-toastify";
import 'react-toastify/dist/ReactToastify.css';


const Index = () => {

    const defaultSchema = new Array(1)
    const [schemaOne, setSchemaOne] = useState(defaultSchema)
    const [nwbSchema, setSchema] = useState(defaultSchema);
    const [selectedFile, setSelectedfile] = useState(null);
    const [nwbPath, setNwbpath] = useState(null);
    const pathForm = useRef(null)

    useEffect(() => {
        fetch("/index")
            .then((res) => res.json())
            .then((data) => {
                setSchemaOne(data.schemaOne);
                setSchema(data.schemaTwo);
            });
    }, []);

    const handleSubmit = async (e) => {
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

    const uiSchema = {
        "session_description": {
            "ui:widget": "textarea" // could also be "select"
        }
    };

    // Map forms on data change and return html element with nwb form data
    const nwbForm = useMemo(() => {
        return (
            nwbSchema.map((nwb, index) => {
                if (nwb === 1) {
                    return ''
                }
                return (
                    < Card >
                        <Card.Header>
                            <Accordion.Toggle as={Button} variant="link" eventKey={index + 1}>
                                {Object.keys(nwb)[0]}
                            </Accordion.Toggle>
                        </Card.Header>
                        <Accordion.Collapse eventKey={index + 1}>
                            <Card.Body>
                                <Form key={nwb} schema={Object.values(nwb)[0]} onSubmit={handleSubmit} uiSchema={uiSchema} />
                            </Card.Body>
                        </Accordion.Collapse>
                    </Card >
                )
            })
        )
    }, [nwbSchema])

    // Map forms on data change and return html element with inputs form data
    const inputsForm = useMemo(() => {
        return (
            schemaOne.map((schema, index) => {
                if (schema === 1) {
                    return ''
                }
                return (
                    <Row>
                        <Col md={12}>
                            <Card>
                                <Card.Body>
                                    <Form schema={Object.values(schema)[0]} onSubmit={handleSubmit} />
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>
                )
            })
        )
    }, [schemaOne])

    const handleLoad = async (e) => {
        setSelectedfile(e.target.files[0])
    };

    const submitFile = choice => async (e) => {
        e.preventDefault()

        const payload = new FormData();
        payload.append(
            choice,
            selectedFile,
        );

        const res = await siteContent.sendFile(payload)

        if (res.ok) {
            toast.success('Metadata Uploaded');
            setSelectedfile(null)
            if (choice === 'nwb') {
                setSchema(res.data.schemaTwo)
            } else {
                setSchemaOne(res.data.schemaOne)
            }

        } else {
            toast.error("Something went wrong.");
        }
    }

    const clearSchema = choice => async e => {
        e.preventDefault()

        const payload = {
            "formTitle": 'clear',
            "formChoice": choice
        }
        const res = await siteContent.sendForm(payload)

        if (res.ok) {
            toast.success('Schema Cleaned');
            if (choice === 'nwb') {
                setSchema(defaultSchema)
            } else {
                setSchemaOne(defaultSchema)
            }
        }
        else {
            toast.error("Something went wrong.");
        }
    }

    const convertNwb = async (e) => {
        e.preventDefault()
        if (nwbPath !== null) {
            const payload = {
                nwbPath
            }
            const res = await siteContent.sendPath(payload)

            if (res.ok) {
                toast.success('Converted');
                setNwbpath(null)
                pathForm.current.reset();
            } else {
                toast.error('Something went wrong')
            }
        } else {
            toast.error("Path field must not be empty.");
        }
    }


    return (
        <Styles>
            <Container fluid>
                <Row>
                    <Col md={{ span: 10, offset: 1 }}>
                        <Card>
                            <Card.Body>
                                <FormReact onSubmit={submitFile('input')}>
                                    <FormReact.Group>
                                        <FormReact.File label="Load Input Metadata" onChange={handleLoad} />
                                        <Button type='submit' className='btn btn-info'>Submit</Button>
                                        <Button onClick={clearSchema('input')} className='btn btn-info'>Clear Schema</Button>
                                    </FormReact.Group>
                                </FormReact>
                            </Card.Body>
                        </Card>
                    </Col>
                </Row>
                <Row>
                    <ToastContainer />
                    <Col md={{ span: 10, offset: 1 }}>
                        {inputsForm}
                    </Col>
                </Row>
            </Container>
            <Container fluid>
                <Row>
                    <Col md={{ span: 10, offset: 1 }}>
                        <Card>
                            <Card.Body>
                                <FormReact onSubmit={submitFile('nwb')}>
                                    <FormReact.Group>
                                        <FormReact.File label="Load NWB Metadata" onChange={handleLoad} />
                                        <Button type='submit' className='btn btn-info'>Submit</Button>
                                        <Button onClick={clearSchema('nwb')} className='btn btn-info'>Clear Schema</Button>
                                    </FormReact.Group>
                                </FormReact>
                            </Card.Body>
                        </Card>
                    </Col>
                </Row>
                <Row>
                    <Col md={{ span: 10, offset: 1 }}>
                        <Accordion>
                            {nwbForm}
                        </Accordion>
                    </Col>
                </Row>
                <Row>
                    <Col md={{ span: 10, offset: 1 }}>
                        <FormReact ref={pathForm} onSubmit={convertNwb}>
                            <FormReact.Group>
                                <FormReact.Label>Save Path</FormReact.Label>
                                <FormReact.Control placeholder='Path/to/file.nwb' onChange={(e) => setNwbpath(e.target.value)} />
                                <Button type='submit' className='btn btn-info'>Convert</Button>
                            </FormReact.Group>
                        </FormReact>
                    </Col>
                </Row>
            </Container>
        </Styles >
    )
}

export default Index;