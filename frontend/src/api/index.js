import { create } from "apisauce";

const api = create({
    baseURL: 'http://localhost:5000', // eslint-disable-line
});

export const siteContent = {
    sendForm: (p) => api.post("/index/savemetadata", p),
    sendPath: (p) => api.post("/index/convertnwb", p),
    sendFile: (p) => api.post("index/uploadfile", p),
}