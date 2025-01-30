import {config} from "../js/config.js";
import {notifier} from "../js/notifier.js";
import {refreshToken, getToken} from "../js/index.js";


function overlayDragOverHandler(event){
    event.preventDefault();
    document.getElementById("file-overlay").classList.add("activated");
}

function overlayDragLeaveHandler(event){
    document.getElementById("file-overlay").classList.remove("activated");
}


function fileDragOverHandler(event){
    event.preventDefault();
    document.getElementById("file-window").classList.add("highlighted");
    document.getElementById("file-overlay").classList.add("activated");
}

function fileDragLeaveHandler(event){
    document.getElementById("file-window").classList.remove("highlighted");
    document.getElementById("file-overlay").classList.remove("activated");
}

let isUploading = false;

async function onStartUploading(){
    const fileWindowInner = document.getElementsByClassName("file-window-inner")[0];
    fileWindowInner.style.display = "none";
    
    const loadingPanel = document.getElementsByClassName("file-loading-animation")[0];
    loadingPanel.style.display = "flex";
}

let historyItem = null;
const historyPanel = document.getElementsByClassName("history-panel")[0];
const historyList = historyPanel.getElementsByClassName("history-list")[0];

function setAnimationOfHistory(){
    historyList.innerHTML = "";
    historyList.style.display = "none";
    historyPanel.getElementsByClassName("text-empty")[0].style.display = "none";
    historyPanel.getElementsByClassName("loading-animation")[0].style.display = "flex";
}

function setEmptyHistory(){
    historyList.innerHTML = "";
    historyList.style.display = "none";
    historyPanel.getElementsByClassName("loading-animation")[0].style.display = "none";
    historyPanel.getElementsByClassName("text-empty")[0].style.display = "flex";
}

async function updateHistory(){
    setAnimationOfHistory();
    const url = `${config["base-host"]}/archivator/files-list`;
    const token = await getToken();
    if (!token){
        setEmptyHistory();
        return;
    };

    const resp = await fetch(url, {
        headers : {
            "Authorization" : token,
        }
    })
    if (!resp.ok) {
        setEmptyHistory();
        return;
    }
    let userFiles = await resp.json();
    if (userFiles.length == 0){
        setEmptyHistory();
        return;
    }
    userFiles = userFiles.slice(0, 11);
    
    if (!historyItem){
        const url = `${config["base-host"]}/archivator/history-item`;
        const resp = await fetch(url);
        if (resp.status != 200) {
            setEmptyHistory();
            return;
        };

        const respText = await resp.text();
        const parsed = (new DOMParser()).parseFromString(respText, "text/html");
        historyItem = parsed.body.firstChild;
    }

    userFiles.forEach(element => {
        const newItem = historyItem.cloneNode(true);
     
        let fileName = element["original_name"];
        if (fileName.length >= 20){
            fileName = fileName.slice(0, 17) + "..."
        }
        const fileId = element["file_id"];
        const fileType = element["file_type"];
        // const downloadTime = element["download_time"];
        
        const file_type_converts = {"archive" : "Файл", "any_file" : "Архив"}
        
        newItem.getElementsByClassName("file-name")[0].innerHTML = fileName;
        newItem.getElementsByClassName("file-type")[0].innerHTML = file_type_converts[fileType];
        newItem.getElementsByClassName("file-download")[0].id = fileId;
        
        historyList.appendChild(newItem);
    });
    
    historyPanel.getElementsByClassName("loading-animation")[0].style.display = "none";
    historyList.style.display = "block";
}

async function onEndUploading(status){
    const loadingPanel = document.getElementsByClassName("file-loading-animation")[0];
    loadingPanel.style.display = "none";

    const fileWindowInner = document.getElementsByClassName("file-window-inner")[0];
    fileWindowInner.style.display = "flex";

    if (status == 200) await updateHistory();
}


async function uploadFile(file){
    const url = `${config["base-host"]}/archivator/archivate/`;
    const formData = new FormData();
    formData.append("file", file);

    const xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    
    const accessToken = await getToken();
    if (!accessToken) return;

    xhr.setRequestHeader("Authorization", accessToken);
    xhr.onloadend = async function(){
        if (xhr.status == 401){
            notifier("Токена нет", "debug");
            let success = await refreshToken();
            console.log(success);
            if (!success) {
                isUploading = false;
                return;
            }
            
            await uploadFile(file)
            return;
        }
        else{
            isUploading = false;
        }
        console.log(xhr.responseText)
        await onEndUploading(xhr.status);
    }
    xhr.send(formData);
}

async function fileDropHandler(event){
    event.preventDefault()  

    fileDragLeaveHandler(event);
    let items = Array.from(event.dataTransfer.items);
    console.log(items);
    let file = null;
    for (let i = 0; i < items.length; i++){
        let curItem = items[i];
        if (curItem.kind == "file"){
            file = curItem.getAsFile();
            break;
        }
    }
    if (!file) return;
    if (file.size > config["max-file-size-bytes"]){
        const errorMessage = "Файл превышает 100мб";
        notifier(errorMessage, "error");
        return;
    }
    if (isUploading) return;
    isUploading = true;
    notifier("Файл получен", "debug")

    await onStartUploading();
    await uploadFile(file);
}

function handlersConnecting(){
    const fileOverlay = document.getElementById("file-overlay");
    const fileWindow = document.getElementById("file-window");
    
    fileOverlay.addEventListener("dragover", overlayDragOverHandler);
    fileOverlay.addEventListener("dragleave", overlayDragLeaveHandler);
    
    fileWindow.addEventListener("dragover", fileDragOverHandler);
    fileWindow.addEventListener("dragleave", fileDragLeaveHandler);
    fileWindow.addEventListener("drop", fileDropHandler);       
}
handlersConnecting();
updateHistory();