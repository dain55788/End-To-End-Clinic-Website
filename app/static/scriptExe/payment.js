document.getElementById('submit').addEventListener('click', submitForm)
async function submitForm(){
    const response = await fetch ('/create_payment_link', {
    method:'post'
    })
    const payment = await response.json()
    window.location.href = payment.checkoutUrl;
}