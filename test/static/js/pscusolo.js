//Global constants
const buttonOn = "btn-success";
const buttonOff = "btn-danger";
const colorOk = "#5cb85c";
const colorFail = "#d9534f";
const colorUnknown = '#555555';
const colorWarn = "#ffa500"

function round1dp(flt)
{
    //return Math.round(flt * 10) / 10;
    return flt.toFixed(1);
}

function generateTempSensors(count)
{
    var ret = `
  <div class="caption">
    <div class="container-fluid">
      <div class="row"><h4>Temperature:</h4></div>
      <div class="row caption-row">
        <div class="col-xs-5">Status:</div>
        <div id="tmp-health" class="col-xs-5 status vertical-align">&nbsp;</div>
      </div>
      <div class="row caption-row">
        <div class="col-xs-5">Latched:</div>
        <div id="tmp-latched"  class="col-xs-5 status vertical-align">&nbsp;</div>
      </div>
    </div>
  </div>
  <table class="table table-striped">
  <thead>
    <tr>
      <th class="text-left"   style="width:25%;">Sensor</th>
      <th class="text-center" style="width:18.75%;">Value</th>
      <th class="text-center" style="width:18.75%;">Setpoint&nbsp;Over</th>
      <th class="text-center" style="width:12.5%;">Setpoint&nbsp;Under</th>
      <th class="text-center" style="width:12.5%;">Tripped&nbsp;Over</th>
      <th class="text-center" style="width:12.5%;">Tripped&nbsp;Under</th>
    </tr>
    </thead>
  <tbody>
   `;

    for(id = 0; id < count; ++id)
    {
        ret += `
          <tr>
            <th class="text-left"><span id="tmp${id}-name"></span></th>
            <td><span id="tmp${id}-tmp"></span></td>
            <td><span id="tmp${id}-set-over"></span></td>
            <td><span id="tmp${id}-set-under"></span></td>
            <td><div id="tmp${id}-trip-over" class="status"></div></td>
            <td><div id="tmp${id}-trip-under" class="status"></div></td>
          </tr>
        `;
    }

    ret += "</tbody></table>";

    return ret;
}

class TempSensor
{
    constructor(id)
    {
        this.id = id;
        this.map = new Map();
        this.active = true;

        var elements = document.querySelectorAll(`[id^='tmp${id}-']`);
        for (var i = 0; i < elements.length; ++i)
        {
            var start = 4 + id.toString().length;
            var key = elements[i].id.substr(start,
                                            elements[i].id.length - start);
            this.map.set(key, elements[i]);
        }
    }

    update(data)
    {
        var temperatureVal = '';
        var setpointoverVal = '';
        var setpointunderVal = '';
        temperatureVal = round1dp(data.temperature) + '°C';
        setpointoverVal = round1dp(data.setpoint_over) + '°C';
        setpointunderVal = round1dp(data.setpoint_under) + '°C';
        this.map.get("name").innerHTML = data.sensor_name;
        this.map.get("tmp").innerHTML = temperatureVal;
        this.map.get("set-over").innerHTML = setpointoverVal;
        this.map.get("set-under").innerHTML = setpointunderVal;
        this.map.get("trip-over").style.backgroundColor = data.trip_over ? colorFail : colorOk;
        this.map.get("trip-under").style.backgroundColor = data.trip_under ? colorFail : colorOk;
    }
}

function generateHumiditySensors(h_count)
{
    var ret = `
      <div class="caption">
	<div class="container-fluid">
	  <div class="row"><h4>Humidity:</h4></div>
	  <div class="row caption-row">
	    <div class="col-xs-5">Status:</div>
	    <div id="h-health" class="col-xs-5 status vertical-align">&nbsp;</div>
	  </div>
	  <div class="row caption-row">
	    <div class="col-xs-5">Latched:</div>
	    <div id="h-latched"  class="col-xs-5 status vertical-align">&nbsp;</div>
	  </div>
	</div>
      </div>
      <table class="table table-striped">
	<thead>
	  <tr>
	    <th class="text-left"   style="width:25%;">Sensor</th>
	    <th class="text-center" style="width:18.75%;">Value</th>
	    <th class="text-center" style="width:18.75%;">Setpoint&nbsp;Over</th>
      <th style="width:12.5%;"></th>
	    <th class="text-center" style="width:12.5%;">Tripped&nbsp;Over</th>
      <th style="width:12.5%;"></th>
	  </tr>
	</thead>
      <tbody>
    `;

    for(id = 0; id < h_count; ++id)
    {
        ret += `
          <tr>
            <th class="text-left"><span id="h${id}-name"></span></th>
            <td><span id="h${id}-h"></span></td>
            <td><span id="h${id}-set-over"></span></td>
            <th style="width:12.5%;"></th>
            <td><div id="h${id}-trip-over" class="status"></div></td>
            <th style="width:12.5%;"></th>
          </tr>
        `;
    }

    ret += "</tbody></table>";

    return ret;
}

class HumiditySensor
{
    constructor(id)
    {
        this.map = new Map();
        this.active = true;

        var elements = document.querySelectorAll(`[id^='h${id}-']`);
        for (var i = 0; i < elements.length; ++i)
        {
            var start = 2 + id.toString().length;
            var key = elements[i].id.substr(start,
                                            elements[i].id.length - start);
            this.map.set(key, elements[i]);
        }
    }

    update(data)
    {
        this.map.get("trip-over").style.backgroundColor = data.trip_over ? colorFail : colorOk;
        var humidityValue = round1dp(data.value) + '%';
        var setpointValue = round1dp(data.setpoint_over) + '%';
        this.map.get("name").innerHTML = data.sensor_name;
        this.map.get("h").innerHTML = humidityValue;
        this.map.get("set-over").innerHTML = setpointValue;
    }
}

function generateLeakSensors(l_count)
{
    var ret = `
      <div class="caption">
	<div class="container-fluid">
	  <div class="row"><h4>Leak:</h4></div>
	  <div class="row caption-row">
	    <div class="col-xs-5">Status:</div>
	    <div id="l-health" class="col-xs-5 status vertical-align">&nbsp;</div>
	  </div>
	  <div class="row caption-row">
	    <div class="col-xs-5">Latched:</div>
	    <div id="l-latched"  class="col-xs-5 status vertical-align">&nbsp;</div>
	  </div>
	</div>
      </div>
      <table class="table table-striped">
	<thead>
	  <tr>
	    <th class="text-left"   style="width:25%;">Sensor</th>
	    <th class="text-center" style="width:18.75%;">Value</th>
	    <th class="text-center" style="width:18.75%;">Setpoint&nbsp;Under</th>
      <th style="width:12.5%;"></th>
	    <th class="text-center" style="width:12.5%;">Tripped&nbsp;Under</th>
      <th class="text-center" style="width:12.5%;">Trace</th>
	  </tr>
	</thead>
      <tbody>
    `;

    for(id = 0; id < l_count; ++id)
    {
        ret += `
          <tr>
            <th class="text-left"><span id="l${id}-name"></span></th>
            <td><span id="l${id}-l"></span></td>
            <td><span id="l${id}-set-under"></span></td>
            <th style="width:12.5%;"></th>
            <td><div id="l${id}-trip-under" class="status"></div></td>
            <td><div id="l${id}-trace" class="status"></div></td>
          </tr>
        `;
    }

    ret += "</tbody></table>";

    return ret;
}

class LeakSensor
{
    constructor(id)
    {
        this.map = new Map();
        this.active = true;

        var elements = document.querySelectorAll(`[id^='l${id}-']`);
        for (var i = 0; i < elements.length; ++i)
        {
            var start = 2 + id.toString().length;
            var key = elements[i].id.substr(start,
                                            elements[i].id.length - start);
            this.map.set(key, elements[i]);
        }
    }

    update(data)
    {
        this.map.get("trip-under").style.backgroundColor = data.trip_under ? colorFail : colorOk;
        this.map.get("trace").style.backgroundColor = data.trace ? colorOk : colorFail;
        var leakValue = round1dp(data.value) + 'M&#8486';
        var setpointValue = round1dp(data.setpoint_under) + 'M&#8486';
        this.map.get("name").innerHTML = data.sensor_name;
        this.map.get("l").innerHTML = leakValue;
        this.map.get("set-under").innerHTML = setpointValue;
    }
}

function generatePumpSensors(count)
{
    var ret = `
      <div class="caption">
        <div class="container-fluid">
          <div class="row"><h4>Pump:</h4></div>
          <div class="row caption-row">
            <div class="col-xs-5">Status:</div>
            <div id="p-health" class="col-xs-5 status vertical-align">&nbsp;</div>
          </div>
          <div class="row caption-row">
            <div class="col-xs-5">Latched:</div>
            <div id="p-latched"  class="col-xs-5 status vertical-align">&nbsp;</div>
          </div>
          <div class="row caption-row">
            <div class="col-xs-5">Tripped:</div>
            <div id="p-tripped" class="col-xs-5 status vertical-align">&nbsp;></div>
          </div>
        </div>
      </div>
    `;

    return ret;
}

class PumpSensor
{
    constructor(id)
    {
        this.map = new Map();

        var elements = document.querySelectorAll(`[id^='p${id}-']`);
        for (var i = 0; i < elements.length; ++i)
        {
            var start = 2 + id.toString().length;
            var key = elements[i].id.substr(start,
                                            elements[i].id.length - start);
            this.map.set(key, elements[i]);
        }
    }

}

//Add templates to page
var pscusolo_html = "";

pscusolo_html += generateTempSensors(2);
pscusolo_html += generateHumiditySensors(1);
pscusolo_html += generateLeakSensors(1);
pscusolo_html += generatePumpSensors(1);

$("#pscusolo").html(pscusolo_html);

var temp_sensors = [];
var humidity_sensors = [];
var leak_sensors = [];
var fan_sensors = []
var pump_sensor;

var global_elems = new Map();
$(document).ready(function() {

    //Get sensors and cache DOM elements
    for(var i = 0; i < 2; ++i)
        temp_sensors.push(new TempSensor(i));
    for(var i = 0; i < 1; ++i)
        humidity_sensors.push(new HumiditySensor(i));

    for(var i = 0; i < 1; ++i)
        leak_sensors.push(new LeakSensor(i));

    pump_sensor = new PumpSensor(0);

    var elems = document.querySelectorAll("[id$='-health']");
    for(var i = 0; i < elems.length; ++i)
        global_elems.set(elems[i].id, elems[i]);

    var latched_elems = document.querySelectorAll("[id$='-latched']");
    for(var i = 0; i < latched_elems.length; i++)
        global_elems.set(latched_elems[i].id, latched_elems[i]);

    global_elems.set("p-tripped", document.querySelector('#p-tripped'));

    global_elems.set("overall-status", document.querySelector("#overall-status"));
    global_elems.set("overall-latched", document.querySelector("#overall-latched"));
    global_elems.set("overall-tripped", document.querySelector("#overall-tripped"));
    global_elems.set("overall-armed", document.querySelector("#overall-armed"));
    global_elems.set("overall-fan1", document.querySelector("#overall-fan1"));
    global_elems.set("overall-fan2", document.querySelector("#overall-fan2"));
    global_elems.set("arm", document.querySelector("#button-arm"));

    //Start update function
    setInterval(updateAll, 500);
});

function update_status_box(el, value, text_true, text_false)
{
    el.style.backgroundColor = value ? colorOk : colorFail;
    el.innerHTML = value ? text_true : text_false;
}

function update_button_state(el, value, text_true, text_false)
{
    el.classList.add(value ? buttonOn : buttonOff);
    el.classList.remove(value ? buttonOff: buttonOn);
    el.innerHTML = value ? text_true : text_false;
}

function updateAll()
{
    $.getJSON('/api/0.1/pscusolo/', function(response) {

        //Handle temp sensors
        for(var i = 0; i < temp_sensors.length; ++i)
            temp_sensors[i].update(response.temperature.sensors[i]);

        //Handle humidity sensors
        for(var i = 0; i < humidity_sensors.length; ++i)
            humidity_sensors[i].update(response.humidity.sensors[i]);

        for(var i = 0; i < leak_sensors.length; ++i)
            leak_sensors[i].update(response.leak.sensors[i]);

        for(var i = 0; i < fan_sensors.length; ++i)
            fan_sensors[i].update(response.fans.sensors[i])

        //Handle overall status
        update_status_box(global_elems.get("overall-status"), response.overall, 'Healthy', 'Error');
        update_status_box(global_elems.get("overall-latched"), !response.latched, 'No', 'Yes');
        update_status_box(global_elems.get("overall-tripped"), !response.tripped, 'No', 'Yes');
        update_status_box(global_elems.get("overall-armed"), response.armed, 'Yes', 'No');

        global_elems.get("overall-fan1").innerHTML = response.fans.sensors[0].value + "&nbsp;rpm";
        global_elems.get("overall-fan2").innerHTML = response.fans.sensors[1].value + "&nbsp;rpm";

        // Handle health states
        update_status_box(global_elems.get("tmp-health"), response.temperature.healthy, 'Healthy', 'Error');
        update_status_box(global_elems.get("h-health"), response.humidity.healthy, 'Healthy', 'Error');
        update_status_box(global_elems.get("l-health"),response.leak.healthy, 'Healthy', 'Error');
        update_status_box(global_elems.get("p-health"), response.pump.healthy, 'Healthy', 'Error');

         // Handle latched states
        update_status_box(global_elems.get("tmp-latched"), !response.temperature.latched, 'No', 'Yes');
        update_status_box(global_elems.get("h-latched"), !response.humidity.latched, 'No', 'Yes');
        update_status_box(global_elems.get("l-latched"), !response.leak.latched, "No", "Yes");
        update_status_box(global_elems.get("p-latched"), !response.pump.latched, 'No', 'Yes')

        // Handle pump trip state
        update_status_box(global_elems.get("p-tripped"), !response.pump.sensors[0].pump_trip, 'No', 'Yes');

        // Handle button states
        update_button_state(global_elems.get("arm"), response.armed, 'Disarm Interlock', 'Arm Interlock');
    });
}

function armInterlock()
{
    $.ajax('/api/0.1/pscusolo/',
           {method: 'PUT',
            contentType: 'application/json',
            processData: false,
            data: JSON.stringify({armed: global_elems.get("arm").classList.contains(buttonOff)})});
}
