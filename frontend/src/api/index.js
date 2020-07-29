import { create } from "apisauce";

const api = create({
    baseURL: 'http://localhost:5000', // eslint-disable-line
});

export const siteContent = {
    getIndex: () => api.get('/index')
}