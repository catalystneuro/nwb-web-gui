import { create } from "apisauce";

const api = create({
    baseURL: 'http://localhost:5000', // eslint-disable-line
});

export const siteContent = {
    sendForm: (p) => api.post("/index", p),
    sendPath: (p) => api.post("/index/savenwb", p)
}