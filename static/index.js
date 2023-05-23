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

var prevLabel = "";
var prevTime = Date.now();
var accumulate = 0;

function updateTextStream(text) {
    const text_split = text.split(" ");
    const label = labels[parseInt(text_split[0])];
    const prob = text_split[1];

    const textStreamElement = document.querySelector('#action_stream');
    const div = document.createElement("pre");
    const textnode = document.createTextNode(label + ' ' + prob);
    div.appendChild(textnode)
    textStreamElement.appendChild(div);

    if (textStreamElement.childNodes.length > 10) {
        textStreamElement.removeChild(textStreamElement.childNodes[0]);
    }

    const labelElement = document.querySelector('#action');
    labelElement.innerHTML = label;
    const objectElement = document.querySelector('#object');
    const temp = label ? label.split(" ") : ["none"];
    objectElement.innerHTML = temp[temp.length - 1];

    if (label && label !== prevLabel) {
        if (prevLabel === "") {
            prevTime = Date.now();
        } else {
            const now = Date.now();
            const reportElement = document.querySelector('#report_stream');
            const dur = (now - prevTime) / 1000;
            reportElement.appendChild(
                createReportEntry(
                    prevLabel,
                    "",
                    dur
                )
            );
            accumulate += dur;
            prevTime = now;
            if (prevLabel == "put in instruction paper") {
                reportElement.appendChild(
                    createReportEntry(
                        "Total",
                        "",
                        accumulate
                    )
                );
            }
        }
        prevLabel = label;
    }
}

const textStreamSource = new EventSource('/label_feed');
textStreamSource.onmessage = function (event) {
    updateTextStream(event.data);
};
