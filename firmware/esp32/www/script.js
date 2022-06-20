//PARAMETERS -------------------------------
const mins = 5
const secs = mins * 60

let last_index = 0


// COLORS -----------------------------------
const accent = '#fa423b'
const bg = '#212429'

// GLOBAL CHARTS SETTINGS -------------------
const options = {
    scales: {
        x: {
            grid: {
                color: bg,
            },
            ticks: {
                color: 'white'
            }
        },
        y: {
            grid: {
                color: bg,
            },
            ticks: {
                color: 'white'
            }
        }
    },
    responsive: true,
    //maintainAspectRatio: false
}

// GLOBAL VARS ANS DOM OBJECTS --------
let inst_values = [0.0, 0.0, 0.0, 0.0, 0.0]
const measure_cards = document.querySelectorAll(".measure_card>.card_inner");
const menu_items = document.querySelectorAll(".menu_item")

// 24H CHART ----------------------------------
const chart24h_ctx = document.getElementById("24h_chart")
const chart24h_data = [{
    label: 'Voltage',
    data: [],
    fill: false,
    borderColor: accent,
    tension: 0.2,
},
{
    label: 'Current',
    data: [],
    fill: false,
    borderColor: accent,
    tension: 0.2,
},
{
    label: 'Frequency',
    data: [],
    fill: false,
    borderColor: accent,
    tension: 0.2,
},
{
    label: 'Power',
    data: [],
    fill: false,
    borderColor: accent,
    tension: 0.2,
},
{
    label: 'Phase angle',
    data: [],
    fill: false,
    borderColor: accent,
    tension: 0.2,
},
]
const chart24h = new Chart(chart24h_ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [chart24h_data[0]]
    },
    options: options
})

// GENERIC FUNCTIONS --------------------
function update_cards() {
    measure_cards.forEach((card, index) => {
        card.querySelector('.value').innerText = inst_values[index];
    })
}

function start_chart(socket) {
    console.log("chart s")
    //get data from the last 24h
    now = Math.floor(Date.now() / 1000);
    old_last = Math.floor(now / secs) * secs; //get data from the nearest multiple of mins
    socket.send("chart-from-to:" + (old_last - 24 * 3600) + ":" + old_last)
};

// WEBSOCKET ---------------------------

let ip = window.location.hostname
let socket = new WebSocket("ws://" + ip);


socket.onopen = function (event) {
    console.log("websocket connected");
    //richiesta dati grafico solo dopo la connessione del socket
    start_chart(socket)
};

socket.onmessage = function (event) {
    e = JSON.parse(event.data)
    console.log(e)
    if (e.type == 'measures') {
        values_arr = e.content;
        inst_values[0] = values_arr[0].toFixed(2);
        inst_values[1] = values_arr[1].toFixed(2);
        inst_values[2] = values_arr[2].toFixed(2);
        inst_values[3] = (values_arr[0] * values_arr[1]).toFixed(3);
        inst_values[4] = String(values_arr[3]);
        update_cards()
    } else if (e.type == "chart-init") {
        console.log("init")
        chart24h.data.labels = []
        chart24h_data.forEach(ds => {
            ds.data = []
        })
    } else if (e.type == "chart-append") {
        date = new Date(e.content.timestamp * 1000);
        label = ("0" + date.getHours()).slice(-2) + ":" + ("0" + date.getMinutes()).slice(-2);
        chart24h.data.labels.push(label)
        values_arr = e.content.measures;
        values = [
            values_arr[0],
            values_arr[1],
            values_arr[2],
            values_arr[0] * values_arr[1],
            values_arr[3],
        ]
        chart24h_data.forEach((ds, index) => {
            ds.data.push(values[index])
        })
    } else if (e.type == "chart-init-stop") {
        console.log("stopped")
        chart24h.data.datasets = [chart24h_data[0]]
        console.log(chart24h.data)
        chart24h.update()
    } else if (e.type == "chart-add") {
        date = new Date(e.content.timestamp * 1000);
        label = ("0" + date.getHours()).slice(-2) + ":" + ("0" + date.getMinutes()).slice(-2);
        chart24h.data.labels.push(label)
        chart24h.data.labels.shift()
        alues_arr = e.content.measures;
        values = [
            values_arr[0],
            values_arr[1],
            values_arr[2],
            values_arr[0] * values_arr[1],
            values_arr[3],
        ]
        chart24h_data.forEach((ds, index) => {
            ds.data.push(values[index]);
            ds.data.shift();
        })
        chart24h.data.datasets = [chart24h_data[last_index]]
        chart24h.update()

    }
};

socket.onclose = function (event) {
    console.log("websocket closed")
};

// CARDS AND MENU SELECTION

menu_items.forEach(item => {
    item.addEventListener("click", function () {
        document.querySelector(".menu_item_active").classList.remove("menu_item_active");
        item.classList.add("menu_item_active");
    })
})

measure_cards.forEach((card, index) => {
    card.addEventListener("click", function () {
        document.querySelector('.card_active').classList.remove('card_active')
        card.classList.add('card_active')
        last_index = index
        chart24h.data.datasets = [chart24h_data[index]]
        chart24h.update()
    })
})