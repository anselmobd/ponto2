import axios from "axios";

export const axiosPublic = axios.create({
  baseURL: import.meta.env.VITE_API_ENDPOINT,
  headers: {
    "Content-Type": "application/json",
  },
  xsrfHeaderName: "X-CSRFTOKEN",
  xsrfCookieName: "csrftoken"
});
