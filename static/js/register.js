
// Radio button uncheck JQuery

$('input[type="radio"]').mousedown(function() { 
    // if it was checked before
    if(this.checked) {
        $(this).mouseup(function() {  
            // bind param, because "this" will point somewhere else in setTimeout
            var radio = this;
            // apparently if you do it immediatelly, it will be overriden, hence wait a tiny bit
            setTimeout(function() { 
                radio.checked = false; 
            }, 5); 
            $(this).unbind('mouseup');
        });
    }
});