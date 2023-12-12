setTimeout(function () {
  document.getElementById("flash").style.display = "none";
}, 4000);

async function chartIt() {
  const data = await getData(); // Get resulting data from the getData() function.
  if (data.xs === undefined || data.xs.length == 0) {
    alert("Cannot make an analysis due to data is too small");
    return;
  }
  const ctx = document.getElementById("myChart").getContext("2d");
  const myChart = new Chart(ctx, {
    type: "line", // Switch the graph to a line chart
    data: {
      labels: data.xs, // Customize the label sources
      datasets: [
        {
          label: "Monthly amount of transactions", // new name
          data: data.ys, // Customize the data source for the Y-axis
          fill: false, // Do not fill the line
          backgroundColor: "rgba(255, 99, 132, 0.2)", // Adopt single color scheme across different datasets
          borderColor: "rgba(255, 99, 132, 1)", // adopt single color scheme across different datasets
          borderWidth: 1,
        },
      ],
    },
    options: {
      scales: {
        yAxes: [
          {
            ticks: {
              // Include a $ sign in the ticks
              callback: function (value, index, values) {
                return value + "$";
              },
            },
          },
        ],
      },
    },
  });
}
window.addEventListener("DOMContentLoaded", async (event) => {
  const el = document.getElementById("show_button");
  if (el) {
    el.addEventListener("click", chartIt);
    const data = await getData();
    el.addEventListener("click", function () {
      if (data.xs === undefined || data.xs.length == 0) {
        return;
      }
      $(".option").toggle("show");
    });
  }
});
