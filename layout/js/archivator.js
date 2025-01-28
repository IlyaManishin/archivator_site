import {config} from "../js/config.js";
import {notifier} from "../js/notifier.js";
import {refreshToken} from "../js/index.js";

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

async function onEndUploading(status){
    const loadingPanel = document.getElementsByClassName("file-loading-animation")[0];
    loadingPanel.style.display = "none";

    const fileWindowInner = document.getElementsByClassName("file-window-inner")[0];
    fileWindowInner.style.display = "flex";
}


async function uploadFile(file){
    const url = `${config["base-host"]}/archivator/archivate/`;
    const formData = new FormData();
    formData.append("file", file);

    const xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    
    const accessToken = localStorage.getItem("access-token");
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