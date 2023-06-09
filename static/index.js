const labels = [
    "open phone box",
    "take out phone",
    "take out instruction paper",
    "take out earphones",
    "take out charger",
    "put in charger",
    "put in earphones",
    "put in instruction paper",
    "inspect phone",
    "put in phone",
    "close phone box",
    "no action"
];
const objects = [
    "phonebox",
    "phone",
    "not phone",
    "not phone box",
    "both phone and phonebox"
];

function htmlToElement(html) {
    var template = document.createElement('template');
    html = html.trim(); // Never return a text node of whitespace as the result
    template.innerHTML = html;
    return template.content.firstChild;
}

function createReportEntry(label, start, duration, is_mistake) {
    const htmlString = `
    <div class="action-report ${is_mistake ? 'mistake' : ''}">
        <div class="action">${label}</div>
        <div class="start-time">${start}</div>
        <div class="duration">${duration}s</div>
    </div>`;
    return htmlToElement(htmlString);
}

function createWarningEntry(type, message) {
    if (type == 'missing') {
        return htmlToElement(
            `<div class="process-error-missing">
            Thiếu hành động: ${message}
            </div>`
        );
    } else if (type == 'ordering') {
        return htmlToElement(
            `<div class="process-error-ordering">
            Hành động lỗi: ${message}
            </div>`
        );
    }
}

function showTime() {
    var date = new Date();
    var h = date.getHours(); // 0 - 23
    var m = date.getMinutes(); // 0 - 59
    var s = date.getSeconds(); // 0 - 59
    m = (m < 10) ? "0" + m : m;
    s = (s < 10) ? "0" + s : s;
    var time = h + ":" + m + ":" + s;
    document.getElementById("clock_display").innerText = time;
    document.getElementById("clock_display").textContent = time;
    setTimeout(showTime, 1000);
}
showTime();


function updateActionLogs(text) {
    const text_split = text.split(" ");
    const action = labels[parseInt(text_split[0])];
    const prob = text_split[1];
    const object = text_split[2];

    // Display logs
    const textStreamElement = document.querySelector('#action_stream');
    const div = document.createElement("pre");
    const textnode = document.createTextNode(action + ' ' + prob);
    div.appendChild(textnode)
    textStreamElement.appendChild(div);
    if (textStreamElement.childNodes.length > 10) {
        textStreamElement.removeChild(textStreamElement.childNodes[0]);
    }

    const objectElement = document.querySelector('#object');
    objectElement.innerHTML = object //[parseInt(object)];
}

const textStreamSource = new EventSource('/label_feed');
textStreamSource.onmessage = function (event) {
    updateActionLogs(event.data);
};


let prevLabel = "no action";
let prevTime = Date.now();
let accumulate = 0;
function updateProcessReport(data) {
    let label = labels[parseInt(data.label)];
    label = label ? label : "no action";
    if (label == prevLabel) {
        return;
    }

    const labelElement = document.querySelector('#action');
    labelElement.innerHTML = label;

    const reportElement = document.querySelector('#report_stream');
    const lastElementTime = reportElement.children[0]?.querySelector(".duration");
    const now = Date.now();
    const dur = (now - prevTime) / 1000;

    if (lastElementTime) {
        lastElementTime.innerHTML = dur + "s";
    }
    if (prevLabel == "no action") {
        reportElement.prepend(createReportEntry(label, "", "...", data.is_mistake));
        accumulate += dur;
    } else if (prevLabel != "close phone box") {
        reportElement.prepend(createReportEntry(label, "", "...", data.is_mistake));
        accumulate += dur;
    } else {
        reportElement.prepend(createReportEntry("Total", "", accumulate, false));
        accumulate = 0;
    }
    prevTime = now;
    prevLabel = label;

    if (data.is_mistake) {
        let noti = document.querySelector("#notification_area");
        noti.appendChild(createWarningEntry("ordering", label))
    }
}


function clearNotification() {
    let target = document.querySelector("#notification_area");
    while (target.hasChildNodes()) {
        target.removeChild(target.firstChild);
    }
}


function notifyMissingActions(data) {
    // if (checked.length < 11) {
    //     let noti = document.querySelector("#notification_area");
    //     let missing = Array(11).fill(0);
    //     checked.forEach(l => missing[l] = 1);
    //     for (const [index, element] of missing.entries()) {
    //         if (element == 0) {
    //             noti.appendChild(createWarningEntry("missing", labels[index]))
    //         }
    //     }
    // }
    let noti = document.querySelector("#notification_area");
    for (const node of noti.querySelectorAll(".process-error-missing")) {
        noti.removeChild(node);
    };
    for (const action of data.actions) {
        noti.appendChild(createWarningEntry("missing", labels[action]))
    }
}


let socket = io();
socket.on('connect', () => console.log('Connected to client!'));
socket.on('state-changed', updateProcessReport);
socket.on('missed-actions', notifyMissingActions);
