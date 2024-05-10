
function get_data(stat, version) {
    // make a request with ajax
    $.ajax({
        url: '/get_stat_data/' + stat + '/' + version,
        type: 'GET',
        success: function(result) {
            // check if the verion has been found
            if (result == 'not found') {
                console.log('Version not found');
                return;
            }
            
            // create the charts
            create_chart(stat, result);

        },
        error: function(error) {
            console.log(error);
        }
        
    });
}

function create_chart(stat, result) {

    if (stat == 'turnout') {

        xValues = Object.keys(result);
        data = {"monday": [], "tuesday": [], "wednesday": [], "thursday": [], "friday": [], "saturday": [], "sunday": []};
        
        // get a list of number of viewers for each day of the week
        for (let i = 0; i < xValues.length; i++) {
            for (const [key, value] of Object.entries(result[xValues[i]])) {
                data[key].push(value);
            }
        }
        
        new Chart('turnout_chart', {
            type: "line",
            data: {
                labels: xValues,
                
                datasets: [{
                    data: data["monday"],
                    borderColor: "green",
                    fill: false,
                    label: 'Monday'
                },
                {
                    data: data["tuesday"],
                    borderColor: "blue",
                    fill: false,
                    label: 'Tuesday'
                },
                {
                    data: data["wednesday"],
                    borderColor: "red",
                    fill: false,
                    label: 'Wednesday'
                },
                {
                    data: data["thursday"],
                    borderColor: "yellow",
                    fill: false,
                    label: 'Thursday'
                },
                {
                    data: data["friday"],
                    borderColor: "purple",
                    fill: false,
                    label: 'Friday'
                },
                {
                    data: data["saturday"],
                    borderColor: "orange",
                    fill: false,
                    label: 'Saturday'
                },
                {
                    data: data["sunday"],
                    borderColor: "pink",
                    fill: false,
                    label: 'Sunday'
                }
                ]
            },
            options: {
                elements: {
                    point:{
                        radius: 0
                    }
                },
                plugins:{
                    legend: {
                        display: false
                    }
                }
            } 
        });
    
    }

    else if (stat == 'watched-channels') {
        xValues = Object.keys(result);
        yValues = Object.values(result);

        new Chart('watched_channels_chart', {
            type: "bar",
            data: {
                labels: xValues,
                datasets: [{
                    data: yValues,
                    backgroundColor: "red",
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                },]
            },
            options: {
                plugins:{
                    legend: {
                        display: false
                    }
                }
            } 
        });
    } 
    
    else if (stat == 'emotes-ratio'){
        xValues = Object.keys(result);

        // sort the data by ratio and take the top 10
        xValues.sort(function(a, b) {
            return result[b] - result[a];
        });
        xValues = xValues.slice(0, 10);

        data = [];
        for (let i = 0; i < xValues.length; i++) {
            data.push(result[xValues[i]]);
        }

        new Chart('emotes_ratio_chart', {
            type: "bar",
            data: {
                labels: xValues,
                datasets: [{
                    data: data,
                    backgroundColor: "red",
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                },]
            },
            options: {
                plugins:{
                    legend: {
                        display: false
                    }
                },
            } 
        });
    }

}
