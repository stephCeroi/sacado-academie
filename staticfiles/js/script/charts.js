define(['jquery','bootstrap_popover', 'bootstrap','chart'], function ($) {
$(document).ready(function () {
 
 
        console.log("---- NEW test ajax-charts.js ---") ;  

 

 
var dates     = document.getElementById("dates").value; 
var averages  = document.getElementById("averages").value;
var numbers    = document.getElementById("numbers").value;

function convert_to_list(scoresbarSet){
    liste_score_b_n = []
    liste_score_b = scoresbarSet.split("-");

    liste_score_b.forEach( (item) =>{ 
        item_int = parseInt(item);
        if (!isNaN(item_int))
            {liste_score_b_n.push(item_int);}
    });

    return liste_score_b_n
}


var dates_to_read    = convert_to_list(dates); 
var averages_to_read = convert_to_list(averages);
var numbers_to_read  = convert_to_list(numbers);
var barColors = ["violet", "violet","violet","violet","violet", "violet","violet","violet","violet", "violet","violet","violet","violet", "violet","violet","violet"];

new Chart("myChart", {
  type: "bar",
  data: {
    labels: dates_to_read,
    datasets: [{
      backgroundColor: barColors,
      data: numbers_to_read
    }]
  },
  options: {
    legend: {display: true},
    title: {
      display: true,
      text: "Mois Aout"
    }
  }
});
 
 




    });
});
 
