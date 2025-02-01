import { config } from "../js/config.js"
import { notifier } from "./notifier.js";

let contentBlocks = {};
let curContentBlockId = ""
document.addEventListener("DOMContentLoaded", function (event){
    const curContentBlock = document.getElementsByClassName("content-container")[0];
    curContentBlockId = curContentBlock.id;
    
    contentBlocks[curContentBlockId] = curContentBlock;
});

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
    
    try{
        const url = `${config["base-host"]}/authenticate/`;
        const resp = await fetch(url);
        if (!resp.ok) return null;
    
        const newToken = await resp.text();
        localStorage.setItem("access-token", newToken);
        return newToken;
    }catch(error){
        notifier(error, "error");
        return null
    }
}

