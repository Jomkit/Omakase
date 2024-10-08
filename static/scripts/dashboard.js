let $activeOrders = $('.order-active');
let $timestamps = $('.timestamps');
const $orderArea = $('.order-area');

// enable tooltips
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

async function toggleOrder(id, state){
    let res = await axios.patch(`/omakase/api/order/${id}`, {
        "data": {
            "active": state
        }
    });
    location.reload();
}

async function toggleAssistance(id) {
    console.log('clicked');
    const data = {data: {need_assistance: false}};
    await axios.patch(`/omakase/api/order/${id}`, data);

}

$orderArea.on('click', (evt) => {
    if(evt.target.getAttribute('id') == 'toggle-active'){
        if(evt.target.innerText == "Close Order"){
            toggleOrder(evt.target.parentNode.getAttribute('id'), false);
        }
        if(evt.target.innerText == "Open Order"){
            toggleOrder(evt.target.parentNode.getAttribute('id'), true);
        }
    } else if(evt.target.getAttribute('id') == 'toggle-assistance'){
        toggleAssistance(evt.target.parentNode.parentNode.getAttribute('id'));
        evt.target.setAttribute('disabled', true);
    }
})

/** WIP update color status of orders based on elapsed time */
// for(let t of $timestamps){
//     let ts = new Date(t.innerText);
//     let now = new Date().getTime()
//     let dif = now-ts.getTime();
//     let seconds = Math.floor((dif % (1000 * 60)) / 1000);
//     let minutes = Math.floor((dif % (1000 * 60 * 60)) / (1000 * 60));
//     let hours = Math.floor((dif % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
//     console.log(`${hours}:${minutes}:${seconds}`);

// }

// function checkTime(timestamps) {
//     for(t of timestamps){
//         if(t)
//     }
// }
// setInterval(checkTime, 1000);

/** Toggle order active status 
 * 
*/
