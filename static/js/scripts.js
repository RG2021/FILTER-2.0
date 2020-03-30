
//console.log(data);
//var data = [{"starRating": "5.0 out of 5 stars", "reviewTitles": "Best Product On Best Discount", "postDate": "Reviewed in India on 21 February 2020", "names": "Sandeep Chandra", "reviewBody": "Best Product On Best Discount As I Got This 2 Pack Total Of 600gm Best Chocolate Biscuits In Rs 169 (Rs 30 More Combo Discount For Selecting 2 Products & Free Delivery For Prime Membership) Which Makes This Deal Even More Value For Money.Packing Was Great, Delivery Was Great.Taste Is Great As Usual"}];

var app = document.getElementById('root');

var container = document.createElement('div');
container.setAttribute('class', 'container');

app.appendChild(container);

var divdata = document.getElementById('mydiv');
var data = divdata.getAttribute('data-geocode');

var data = JSON.parse(data);

data.sort(function(a, b){
    return b.finalScore - a.finalScore;
});

data.forEach(movie => {
  const card = document.createElement('div');
  card.setAttribute('class', 'card');

  const h1 = document.createElement('h1');
  h1.textContent = movie.reviewTitles;

  const p1 = document.createElement('p');
  p1.textContent = `${movie.names}`;

  const p2 = document.createElement('p');
  p2.setAttribute('class', 'show-read-more');
  p2.textContent = `${movie.reviewBody}`;


  const p3 = document.createElement('p');
  p3.textContent = `${movie.starRating}` + " out of 5 Rating";

  const p4 = document.createElement('p');
  p4.textContent = "On Page Number " + `${movie.Page}`;

  const p5 = document.createElement('p');
  var d = new Date(`${movie.postDate}`);
  p5.textContent = d;



  container.appendChild(card);
  card.appendChild(h1);
  card.appendChild(p1);
  card.appendChild(p2);
  card.appendChild(p3);
  card.appendChild(p4);
  card.appendChild(p5);
})



// Battery Tag:


app = document.getElementById('battery');

container = document.createElement('div');
container.setAttribute('class', 'container');

app.appendChild(container);

var divdatabattery = document.getElementById('mydiv');
var databattery = divdata.getAttribute('data-battery');

var databattery = JSON.parse(databattery);


databattery.forEach(movie => {
  const card = document.createElement('div');
  card.setAttribute('class', 'card');

  const h1 = document.createElement('h1');
  h1.textContent = movie.reviewTitles;

  const p1 = document.createElement('p');
  p1.textContent = `${movie.names}`;

  const p2 = document.createElement('p');
  p2.setAttribute('class', 'show-read-more');
  p2.textContent = `${movie.reviewBody}`;


  const p3 = document.createElement('p');
  p3.textContent = `${movie.starRating}` + " out of 5 Rating";


  container.appendChild(card);
  card.appendChild(h1);
  card.appendChild(p1);
  card.appendChild(p2);
  card.appendChild(p3);
})

