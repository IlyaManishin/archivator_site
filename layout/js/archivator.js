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

function fileDropHandler(event){
    event.preventDefault()  
    console.log(event)  
}