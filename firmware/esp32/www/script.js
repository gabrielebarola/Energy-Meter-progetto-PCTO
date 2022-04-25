const accent = '#fa423b'
const bg = '#212429'

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
    maintainAspectRatio: false
}


ip = window.location.hostname
let socket = new WebSocket("ws://" + ip);
let update_timer
let graph_timer

let inst_values = [0.0, 0.0, 0.0, 0.0, 0.0]

const measure_cards = document.querySelectorAll(".measure_card>.card_inner");
const menu_items = document.querySelectorAll(".menu_item")
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
]
const chart24h = new Chart(chart24h_ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [chart24h_data[0]]
    },
    options: options
})

function update_cards() {
    measure_cards.forEach((card, index) => {
        card.querySelector('.value').innerText = inst_values[index];
    })
}

//WEBSOCKET
function start_update(socket) {
    update_timer = setInterval(function() { socket.send('update_data'); }, 1000);
};

function start_graph(socket) {
    graph_timer = setInterval(function() {
        socket.send('24graph_data');
        chart24h.data.labels = [];
        chart24h.data.datasets.forEach(ds => {
            ds.data = [];
        })
    }, 120000);
};

socket.onopen = function(event) {
    start_update(socket)
    start_graph(socket)
};

socket.onmessage = function(event) {
    e = JSON.parse(event.data)
    if (e.type == 'measures') {
        values_arr = e.content.slice(1, -1).split(", ");
        inst_values[0] = values_arr[0];
        inst_values[1] = values_arr[1];
        inst_values[2] = values_arr[2];
        inst_values[3] = (parseFloat(values_arr[0]) * parseFloat(values_arr[1])).toFixed(3);
        update_cards()
    } else if (e.type == "24chart") {

    }
};

socket.onclose = function(event) {
    clearInterval(update_timer)
    clearInterval(graph_timer)
};

// CARDS SELECTION

menu_items.forEach(item => {
    item.addEventListener("click", function() {
        document.querySelector(".menu_item_active").classList.remove("menu_item_active");
        item.classList.add("menu_item_active");
    })
})

measure_cards.forEach((card, index) => {
    card.addEventListener("click", function() {
        document.querySelector('.card_active').classList.remove('card_active')
        card.classList.add('card_active')
        console.log(index)
        chart24h.data.datasets = [chart24h_data[index]]
        chart24h.update()
    })
})