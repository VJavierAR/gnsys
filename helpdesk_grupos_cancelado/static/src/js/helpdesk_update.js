
function test() {
    console.log("Hola mundo");
    
    ///html/body/div[3]/div/div/div/div[5]/div[5]/h1/span
    var a=document.evaluate('/html/body/div[3]/div/div/div/div[5]/div[6]/table[1]/tbody/tr[19]/td[2]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.innerHTML;
    alert(a);
    //document.getElementsByClassName("o_field_char o_field_widget o_required_modifier field_name").style.color = "red";    
    
}
