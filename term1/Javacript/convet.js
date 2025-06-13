function convert_to_fahrenheit(value){
    value = parseFloat(value)*9/5 + 32
    document.getElementById('result').innerHTML = 'อุณภูมิที่ได้คือ ' + value + ' F'
}
function convert_to_kelvin(value){
    value = parseFloat(value) + 273.15
    document.getElementById('result').innerHTML = 'อุณภูมิที่ได้คือ ' + value + ' K'
}
