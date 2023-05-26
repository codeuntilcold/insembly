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

function createReportEntry(label, start, duration) {
    const htmlString = `
    <div class="action-report">
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
    objectElement.innerHTML = objects[parseInt(object)];
}

const textStreamSource = new EventSource('/label_feed');
textStreamSource.onmessage = function (event) {
    updateActionLogs(event.data);
};


let prevLabel = "";
let prevTime = Date.now();
let accumulate = 0;
let checked = [];
function updateProcessReport(data) {
    let label = labels[parseInt(data.label)]
    let mistake = data.is_mistake ? "mistake" : "";

    // Display label
    const labelElement = document.querySelector('#action');
    labelElement.innerHTML = label;

    // Display action logs
    if (label && label !== prevLabel) {
        if (prevLabel == "") {
            prevTime = Date.now();
        } else {
            const now = Date.now();
            const reportElement = document.querySelector('#report_stream');
            const dur = (now - prevTime) / 1000;
            if (prevLabel != "no action") {
                reportElement.prepend(
                    createReportEntry(
                        prevLabel,
                        mistake,
                        dur
                    )
                );
            }
            accumulate += dur;
            prevTime = now;
            if (prevLabel == "close phone box") {
                reportElement.prepend(
                    createReportEntry(
                        "Total",
                        "",
                        accumulate
                    )
                );
                if (checked.length < 11) {
                    let noti = document.querySelector("#notification_area");
                    let missing = Array(11).fill(0);
                    checked.forEach(l => missing[l] = 1);
                    for (const [index, element] of missing.entries()) {
                        if (element == 0) {
                            noti.appendChild(createWarningEntry("missing", labels[index]))
                        }
                    }
                }
                checked = [];
                accumulate = 0;
                prevLabel = "";
            }
        }
    }
    prevLabel = label;
    checked.push(data.label);

    if (data.is_mistake) {
        let noti = document.querySelector("#notification_area");
        noti.appendChild(createWarningEntry("ordering", label))
    }
}

let socket = io();
socket.on('connect', function () {
    console.log('Connected to client!');
});
socket.on('state-changed', function (data) {
    updateProcessReport(data)
});
// socket.on('add-log', function (data) {
//     updateActionLogs(data)
// })
