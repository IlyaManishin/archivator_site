

export function notifier(message="", type="error"){
    if (!message) return;
    if (type == "debug") {
        console.log(message);
        return;
    }
    const data = {
        "message" : message,
        "type" : type,
    };
    console.log(JSON.stringify(data));
}