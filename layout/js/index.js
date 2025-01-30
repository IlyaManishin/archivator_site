import { config } from "../js/config.js"

export async function refreshToken(){
    const url = `${config["base-host"]}/authenticate/`;
    const resp = await fetch(url);
    if (resp.ok){
        const respData = await resp.json();
        localStorage.setItem("access-token", respData["token"]);
        return true;
    }
    return false;
}

export async function getToken(){
    const checkToken = localStorage.getItem("access-token");
    if (checkToken) return checkToken; 
    
    const url = `${config["base-host"]}/authenticate/`;
    const resp = await fetch(url);
    if (!resp.ok) return null;

    const newToken = await resp.text();
    localStorage.setItem("access-token", newToken);
    return newToken;
}