function showClock(state){
  var nowTime = new Date();
  var nowHour = nowTime.getHours();
  var nowMin  = nowTime.getMinutes();
  if( nowMin < 10 ) {
    nowMin = "0" + nowMin;
  }
  var time = nowHour + ":" + nowMin + state;
  document.getElementById("RealtimeClockArea").innerHTML = time;
}

var msg = document.getElementById("RealtimeClockArea").title;

setInterval(function() {
  showClock(msg);
}, 100);
