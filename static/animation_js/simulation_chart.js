$(document).ready(function (){
    this.chart = null;

    $("#klasyczny").click(() => {
        console.log('this.chart', this.chart);
        if (this.chart && this.chart1 && this.chart2 ) {
            this.chart.destroy();
            this.chart1.destroy();
            this.chart2.destroy();
        }
        getJson('/static/data/data_x.json');
        document.getElementById('Cost').style.display = 'block';
        document.getElementById('Quality').style.display = 'block';
        document.getElementById('CostFuzzy').style.display = 'none';
        document.getElementById('QualityFuzzy').style.display = 'none';
        document.getElementById('object').style.display= 'block';
    });

    $("#rozmyty").click(() => {
        console.log('this.chart', this.chart);
        if (this.chart && this.chart1 && this.chart2) {
            this.chart.destroy();
            this.chart1.destroy();
            this.chart2.destroy();
        }
        getJson('/static/data/data_fuzzy.json');
        document.getElementById('Cost').style.display = 'none';
        document.getElementById('Quality').style.display = 'none';
        document.getElementById('CostFuzzy').style.display = 'block';
        document.getElementById('QualityFuzzy').style.display = 'block';
        document.getElementById('object').style.display= 'block';
    });

    let getJson = (path) => {
        $.getJSON(path, (result) => {
            let labels = result.map(function (e){
                return e.x ;
              }),
                source1 = result.map(function (e){
                  return e.h_z;
                }),
                source2 = result.map(function (e){
                    return e.h;
                }),
                source3 = result.map(function (e){
                    return e.Q_d;
                }),
                source4 = result.map(function (e){
                    return e.Q_o;
                }),
                source5 = result.map(function (e){
                    return e.e;
                });

            let leveltank = document.getElementById('myChart').getContext('2d');

            this.chart = new Chart(leveltank, {
                type:'line',
                data: {
                    labels: labels,
                    datasets:[
                        {
                            label: 'h_z',
                            data: source1,
                            fill: false,
                            lineTension: 0.1,
                            backgroundColor: 'rgba(255, 99, 132, 0.6)',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            borderDash: [5,5]
                        },
                        {
                            label: 'h',
                            data: source2,
                            fill: false,
                            lineTension: 0.1,
                            backgroundColor: 'rgba(54, 162, 235, 0.6)',
                            borderColor: 'rgba(54, 162, 235, 1)'
                        }]
                },
                options:{
                    plugins:{
                        title:{
                            display: true,
                            text: 'Przebieg zmian poziomu substancji w zbiorniku'
                        }
                    }
                }
            });

            let inflowrate = document.getElementById('Chart2').getContext('2d');

            this.chart1 = new Chart(inflowrate, {
                type:'line',
                data: {
                    labels: labels,
                    datasets:[
                        {
                            label: 'Q_d',
                            data: source3,
                            fill: false,
                            lineTension: 0.1,
                            backgroundColor: 'rgba(54, 162, 235, 0.6)',
                            borderColor: 'rgba(54, 162, 235, 1)'
                        },
                        {
                            label: 'Q_o',
                            data: source4,
                            fill: false,
                            lineTension: 0.1,
                            backgroundColor: 'rgba(255, 99, 132, 0.6)',
                            borderColor: 'rgba(255, 99, 132, 1)'
                        }]
                },
                options:{
                    plugins:{
                        title:{
                            display: true,
                            text: 'Przebiegi zmian dopływu i odpływu substancji w zbiorniku'
                        }
                    }
                }
            });

            let error = document.getElementById('Chart3').getContext('2d');

            this.chart2 = new Chart(error, {
                type:'line',
                data: {
                    labels: labels,
                    datasets:[
                        {
                            label: 'e',
                            data: source5,
                            fill: false,
                            lineTension: 0.1,
                            backgroundColor: 'rgba(54, 162, 235, 0.6)',
                            borderColor: 'rgba(54, 162, 235, 1)'
                        }]
                },
                options:{
                    plugins:{
                        title:{
                            display: true,
                            text: 'Przebieg zmian uchybu regulacji'
                        }
                    }
                }
            });

        });
    }
});
