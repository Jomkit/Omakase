let $activeOrders = $('.order-active');
let $timestamps = $('.timestamps');
const $orderArea = $('.order-area');
<<<<<<< HEAD
async function toggleOrder(id, state){
    let res = await axios.patch(`/omakase/api/order/${id}/update`, {
        "data": {
            "active": state
        }
    });
    location.reload();
}

$orderArea.on('click', (evt) => {
    if(evt.target.getAttribute('id') == 'toggle-active'){
        if(evt.target.innerText == "Close Order"){
            toggleOrder(evt.target.parentNode.getAttribute('id'), false);
        }
        if(evt.target.innerText == "Open Order"){
            toggleOrder(evt.target.parentNode.getAttribute('id'), true);
        }
    }
})
=======
>>>>>>> 9337c390882ddbc36641358f2133bb8fa170838e

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
<<<<<<< HEAD
=======
async function toggleOrder(id, state){
    let res = await axios.patch(`omakase/api/order/${id}/update`, {
        "data": {
            "active": state
        }
    });
    location.reload();
}

$orderArea.on('click', (evt) => {
    if(evt.target.getAttribute('id') == 'toggle-active'){
        if(evt.target.innerText == "Close Order"){
            toggleOrder(evt.target.parentNode.getAttribute('id'), false);
        }
        if(evt.target.innerText == "Open Order"){
            toggleOrder(evt.target.parentNode.getAttribute('id'), true);
        }
    }
})
>>>>>>> 9337c390882ddbc36641358f2133bb8fa170838e
