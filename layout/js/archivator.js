import {config} from "../js/config.js"

console.log(config.base-host);

function overlayDragOverHandler(event){
    console.log("hdfdffdfdfdf")
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

function uploadFile(file){
    console.log(file);
}

function fileDropHandler(event){
    event.preventDefault()  

    fileDragLeaveHandler(event);

    let items = Array.from(event.dataTransfer.items);
    let file = null;
    for (let i = 0; i < items.length; i++){
        let curItem = items[i];
        if (curItem.kind == "file"){
            file = curItem;
            break;
        }
    }
    if (!file) return;
    uploadFile(file);
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