var ctx = document.getElementById('confidenceChart').getContext('2d');
var confidence_frequencies = document.getElementById('confidence_container').getAttribute('data-my-variable');
//var frequencies = {{ confidence_frequencies|safe }};  // Assuming this outputs a proper JavaScript array from Django
var stringWithoutBrackets = confidence_frequencies.slice(1, -1);
var arrayStrings = stringWithoutBrackets.split(',');
var confidenceChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['0-10%', '11-20%', '21-30%', '31-40%', '41-50%', '51-60%', '61-70%', '71-80%', '81-90%', '91-100%'],
        datasets: [{
            label: 'Frequency of Confidence Scores',
            data: arrayStrings,
            backgroundColor: 'rgba(54, 162, 235, 0.5)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    stepSize: 1
                }
            }
        }
    }
});