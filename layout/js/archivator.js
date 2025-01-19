import {config} from "../js/config.js"
import {notifier} from "../js/notifier.js"

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

async function onProgressFile(){

}

async function onUploadFile(){

}

async function uploadFile(file){
    const url = `http://${config["base-host"]}/archivator/`;
    const formData = new FormData();
    formData.append("file", file);

    const xhr = new XMLHttpRequest()
    xhr.open("POST", url, true);

    xhr.upload.onprogress = onProgressFile;
    xhr.upload.onload = onUploadFile;

    xhr.onloadend = function(){
        isUploading = false;
    }
    
    xhr.send(formData);
    

    
}

async function fileDropHandler(event){
    event.preventDefault()  

    fileDragLeaveHandler(event);

    let items = Array.from(event.dataTransfer.items);
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