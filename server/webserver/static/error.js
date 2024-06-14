const eventSource = new EventSource("/events");
eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.message.toLowerCase().indexOf("critical") !== -1) {
        window.location.href = "/error/" + data.message; // Redirect the user to the error endpoint
    }
};