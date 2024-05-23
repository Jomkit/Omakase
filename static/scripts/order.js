$menuArea = $('#menu-area');
$billItems = $('#bill-items');
$bill = $('#bill')

function updateSubtotal(costs){
    let subtotal = 0;
    for(i of costs){
        subtotal += parseFloat(i.innerText);
    }
    $('#subtotal-cost')[0].innerText = `$${subtotal.toFixed(2)}`;
    return subtotal;
}

function updateFinalCost(tax, subTotal){
    // Updates final cost after tax
    let finalCost = ((tax * subTotal) + subTotal).toFixed(2);
    $('#final-cost')[0].innerText = `$${finalCost}`;
    return finalCost;
}

function updateAllCost($costs){
    // Updates subtotal, final cost, and tax %
    // Should run at start and when items are added to bill
    let tax = .08;
    let deliveryCost = 5;
    if($('#delivery-cost').length > 0){
        $('#delivery-cost')[0].innerText = `$${deliveryCost.toFixed(2)}`;
    } else{
        deliveryCost = 0;
    }
    $('#taxes')[0].innerText = `${tax * 100}%`;
    
    let subTotal = updateSubtotal($costs);
    subTotal += deliveryCost;
    updateFinalCost(tax, subTotal);
}

async function eventHandler(evt){
    let menuItem = new MenuItem;
    
    // Handle add button click for menu items
    if(evt.target.nodeName == "A"){
        let menuItemId = evt.target.parentNode.getAttribute('id');
    
        await menuItem.putMenuItem(parseInt(menuItemId));
        await order.addToOrder(menuItemId);
        let $costs = $('.cost');
        updateAllCost($costs);
    }
}

class MenuItem {
    constructor(){
        this.baseURL = '/omakase/api/menu';
    }
    async getMenuItem(id){
        let res = await axios.get(`${this.baseURL}/get_menu_item/${id}`);
        return res.data.data;
    }
    async putMenuItem(id, qty=1){
        let details = await this.getMenuItem(id);
        // Check if item already ordered; increment qty if so
        if($(`#${details.id}-qty`).length >= 1){
            let itemQty = parseInt($(`#${details.id}-qty`)[0].innerText);
            itemQty++;
            $(`#${details.id}-qty`)[0].innerText = itemQty;

            $(`.${details.id}-cost`)[0].innerText = (itemQty * details.cost).toFixed(2);
            
            return;
        } else{
            let html = 
            `<tr>
            <th scope="row">${details.name}</th>
            <td id='${details.id}-qty'>${qty}</td>
            <td>$${details.cost}</td>
            <td>$<span class="${details.id}-cost cost">${(qty * details.cost).toFixed(2)}</span></td>
            </tr>`;
            
            let field = $(html);
            $billItems.append(field);
        }
        return;
    }
}

class Order {
    constructor(id){
        this.baseURL = '/omakase/api/order';
        this.id = id;
    }
    async getOrderedItems(){
        let res = await axios.get(`${this.baseURL}/get_order/${this.id}`);
        // console.log(res.data.data.ordered_items);
        return res.data.data.ordered_items;
    }
    async addToOrder(menuItemId){
        let res = await axios.patch(`${this.baseURL}/${this.id}/add_item`, {
            menu_item_id: menuItemId
        });
    }
    async updateBill(){
        let orderedItems = await this.getOrderedItems();
        let m = new MenuItem;
        for(let item of orderedItems){
            await m.putMenuItem(item.item_id, item.qty);
            
        }
        // Really should refactor this, it's in a weird place
        let $costs = $('.cost');
        updateAllCost($costs);
    }
}

function togglePlaceholders(){
    $('#subtotal-cost').toggleClass('placeholder');
    $('#final-cost').toggleClass('placeholder'); 
    $('#delivery-cost').toggleClass('placeholder'); 
    $('#taxes').toggleClass('placeholder');
}

// On start
$currOrder = $('#curr-order').text();
let order = new Order($currOrder);
order.updateBill();
togglePlaceholders();

$menuArea.on('click', eventHandler);

/** flashAssistMsg() sends flash message when assistance button pressed to give user feedback
 * 
 * Should notify staff which order needs assistance
 */
function flashAssistMsg(){
    
    const html = 
    `<div class="container-fluid position-fixed top-0 mt-5 d-flex justify-content-center" style="z-index:1">
    
        <div class="col-6 position-absolute opacity-75 alert alert-info" role="alert">
        Waitstaff will be with you shortly!
        <button type="button" class="btn-close float-end" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>     
        
    </div>`;

    $('nav').after(html);
}

$bill.on('click', (evt) => {
    if(evt.target.getAttribute('id') == "assist-btn"){
        console.log('Assist');
        flashAssistMsg();
    }
});