var ctx = document.getElementById('sentimentChart').getContext('2d');
var sentiment_frequencies = document.getElementById('sentiment_container').getAttribute('sentiment-variable');

const validJsonStr = sentiment_frequencies
  .replace(/u'([^']+)'/g, '"$1"') // Replace u'string' with "string"
  .replace(/'/g, '"'); // Replace any remaining single quotes
let sentimentObj;
try {
    sentimentObj = JSON.parse(validJsonStr);
    console.log(sentimentObj);
} catch (e) {
    console.error('Parsing error:', e);
}
let sentiments = {'Neutral':0,'Positive':0,'Negative':0};
Object.keys(sentiments).forEach(sentiment => {
    if (sentimentObj.hasOwnProperty(sentiment)){
        sentiments[sentiment] = sentimentObj[sentiment];
    }
});

var sentimentChart = new Chart(ctx, {
type: 'pie', // or 'doughnut'
data: {
    labels: ['Neutral', 'Positive', 'Negative'],
    datasets: [{
    label: 'Sentiment Analysis',
    data: [sentiments.Neutral,sentiments.Positive,sentiments.Negative],
    backgroundColor: [
        'rgba(99, 132, 255, 0.6)',
        'rgba(75, 192, 192, 0.6)',
        'rgba(255, 99, 132, 0.6)'
    ],
    borderColor: [
        'rgba(99, 132, 255, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(255, 99, 132, 1)'
    ],
    borderWidth: 1
    }]
},
options: {
    responsive: true,
    maintainAspectRatio: false,
}
});
    