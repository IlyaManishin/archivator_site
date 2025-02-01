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

let historyItemPattern = null;
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
    const token = await getToken();
    if (!token){
        setEmptyHistory();
        return;
    };
    
    let resp;
    try{
        const url = `${config["base-host"]}/archivator/files-list`;
        resp = await fetch(url, {
            headers : {
                "Authorization" : token,
            }
        })
    }
    catch (error){
        notifier(error, "error")
        setEmptyHistory();
        return;
    }
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
    
    if (!historyItemPattern){
        const url = `${config["base-host"]}/archivator/history-item`;
        try{
            const resp = await fetch(url);
            if (!resp.ok) {
                setEmptyHistory();
                return;
            };
            const respText = await resp.text();
            const parsed = (new DOMParser()).parseFromString(respText, "text/html");
            historyItemPattern = parsed.body.firstChild;
        }catch (error){
            setEmptyHistory();
            return;
        }
    }
    userFiles.forEach(element => {
        const newItem = historyItemPattern.cloneNode(true);
     
        let fileName = element["original_name"];
        const maxLength = 35;
        if (fileName.length > maxLength){
            fileName = fileName.slice(0, maxLength - 3) + "...";
        }
        const fileId = element["file_id"];
        const fileType = element["file_type"];
        
        const file_type_converts = {"archive" : "Файл", "any_file" : "Архив"}
        
        newItem.getElementsByClassName("file-name")[0].innerHTML = fileName;
        newItem.getElementsByClassName("file-type")[0].innerHTML = file_type_converts[fileType];

        const downloadButton = newItem.getElementsByClassName("file-download")[0];
        downloadButton.id = fileId;
        const deleteFileButton = newItem.getElementsByClassName("file-delete")[0];
        deleteFileButton.id = fileId;

        
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

let isDeleting = false;
async function deleteFile(file_id){
    const url = `${config["base-host"]}/archivator/file-delete/`;
    const data = {"file_id" : file_id};
    const resp = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type" : "application/json",
            "Authorization" : await getToken(),
        },
        body: JSON.stringify(data),
    });
    const respData = await resp.json();
    if (resp.status != 200) notifier(respData, "debug");
}

let isDownloading = true;
async function downloadFile(file_id){
    const url = `${config["base-host"]}/archivator/file-download/`
    const resp = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type" : "application/json",
            "Authorization" : await getToken(),
        },
        body: JSON.stringify({"file_id" : file_id})
    });
    if (!resp.ok) return;

    const disposition = resp.headers.get("Content-Disposition"); 
    if (!disposition) return;
    
    const filenameMatch = disposition.match(/filename="(.+)"/);
    if (filenameMatch.length == 0) return;
    const filename = filenameMatch[0].replace("filename=", "").replaceAll('"', "");

    const blob = await resp.blob();
    const blob_url = URL.createObjectURL(blob);
    
    const a = document.createElement("a");
    a.style.display = "none";
    a.href = blob_url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
}

function handlersConnecting(){
    const fileOverlay = document.getElementById("file-overlay");
    const fileWindow = document.getElementById("file-window");
    
    fileOverlay.addEventListener("dragover", overlayDragOverHandler);
    fileOverlay.addEventListener("dragleave", overlayDragLeaveHandler);
    
    fileWindow.addEventListener("dragover", fileDragOverHandler);
    fileWindow.addEventListener("dragleave", fileDragLeaveHandler);
    fileWindow.addEventListener("drop", fileDropHandler);       

    const historyPanel = document.getElementsByClassName("history-panel")[0];
    historyPanel.addEventListener("click", async function (event){
        if (event.target.classList.contains("file-delete")){
            isDeleting = true;
            const deleteButton = event.target;
            const file_id = deleteButton.id;
            await deleteFile(file_id);

            const historyItem = deleteButton.parentElement;
            historyItem.remove();
            if (historyPanel.getElementsByTagName("li").length == 0) setEmptyHistory();
            
            isDeleting = false;
        }
        else if (event.target.classList.contains("file-download")){
            isDownloading = true;
            const downloadButton = event.target;
            const file_id = downloadButton.id;
            downloadFile(file_id);
            isDownloading = false;
        }
    })
}
document.addEventListener("DOMContentLoaded", function (){
    handlersConnecting();
    updateHistory();
})