/**
 * Summary Page JavaScript
 * Handles all the dynamic functionality for the Health Check Summary page
 */

document.addEventListener("DOMContentLoaded", function () {
  // Initialize the date range picker
  initDatePicker();

  // Set up initial state
  updatePreview();

  // Add event listeners to dropdowns if they exist
  setupEventListeners();

  // Initialize charts if stats data exists
  initializeCharts();
});

/**
 * Initialize Flatpickr date range picker
 */
function initDatePicker() {
  const dateInput = document.getElementById("time_period");
  if (dateInput) {
    flatpickr("#time_period", {
      mode: "range",
      dateFormat: "d/m/Y",
      allowInput: true,
      onChange: function () {
        updatePreview();
      },
    });
  }
}

/**
 * Set up event listeners for form elements
 */
function setupEventListeners() {
  // Department dropdown change event
  const deptDropdown = document.getElementById("departmentDropdown");
  if (deptDropdown) {
    if (deptDropdown.dataset.role === "Department Leader") {
      deptDropdown.addEventListener("change", onDepartmentChange);
    } else {
      deptDropdown.addEventListener("change", updateTeams);
    }
  }

  // Team dropdown change event
  const teamDropdown = document.getElementById("teamDropdown");
  if (teamDropdown) {
    teamDropdown.addEventListener("change", updateSessions);
  }

  // Session dropdown change event
  const sessionDropdown = document.getElementById("sessionDropdown");
  if (sessionDropdown) {
    sessionDropdown.addEventListener("change", updateProject);
  }

  // Card dropdown change event
  const cardDropdown = document.querySelector('select[name="card"]');
  if (cardDropdown) {
    cardDropdown.addEventListener("change", updatePreview);
  }
}

/**
 * Update teams dropdown based on selected department
 */
function updateTeams() {
  let dept = document.getElementById("departmentDropdown").value;
  fetch(AJAX_URLS.getTeams + "?department_id=" + dept)
    .then((response) => response.json())
    .then((data) => {
      let teamDropdown = document.getElementById("teamDropdown");
      teamDropdown.innerHTML = '<option value="all">All Teams</option>';
      data.teams.forEach(function (team) {
        let label = team.name + " (" + team["department__name"] + ")";
        teamDropdown.innerHTML += `<option value="${team.id}">${label}</option>`;
      });
      updateSessions();
    })
    .catch((error) => console.error("Error fetching teams:", error));
  updatePreview();
}

/**
 * Update sessions dropdown based on selected department and team
 */
function updateSessions() {
  let team = document.getElementById("teamDropdown").value;
  let dept = document.getElementById("departmentDropdown").value;
  fetch(AJAX_URLS.getSessions + "?team_id=" + team + "&department_id=" + dept)
    .then((response) => response.json())
    .then((data) => {
      let sessionDropdown = document.getElementById("sessionDropdown");
      sessionDropdown.innerHTML = '<option value="all">All Sessions</option>';
      data.sessions.forEach(function (session) {
        let label = session.name + " (" + session["team__name"] + ")";
        sessionDropdown.innerHTML += `<option value="${session.id}">${label}</option>`;
      });
      updateProject();
    })
    .catch((error) => console.error("Error fetching sessions:", error));
  updatePreview();
}

/**
 * Update project information based on selected session
 */
function updateProject() {
  let session = document.getElementById("sessionDropdown").value;
  if (session !== "all") {
    fetch(AJAX_URLS.getProject + "?session_id=" + session)
      .then((response) => response.json())
      .then((data) => {
        let projectInfo = document.getElementById("projectInfo");
        if (data.project) {
          projectInfo.innerHTML = `<b>Project assigned to this session:</b> <span style="color:#2774ba;">${data.project.name}</span>`;
        } else {
          projectInfo.innerHTML = "";
        }
      })
      .catch((error) => console.error("Error fetching project:", error));
  } else {
    document.getElementById("projectInfo").innerHTML = "";
  }
  updatePreview();
}

/**
 * Update selection preview card with current dropdown selections
 */
function updatePreview() {
  let dept =
    document.getElementById("departmentDropdown").selectedOptions[0].text;
  let team = document.getElementById("teamDropdown").selectedOptions[0].text;
  let session =
    document.getElementById("sessionDropdown").selectedOptions[0].text;
  let card = document.querySelector('select[name="card"]').selectedOptions[0]
    .text;
  let timePeriod = document.getElementById("time_period").value;

  let html = `<b>Department:</b> ${dept}<br>
                <b>Team:</b> ${team}<br>
                <b>Session:</b> ${session}<br>
                <b>Card:</b> ${card}<br>
                <b>Time Period:</b> ${timePeriod || "-"}`;

  const selectionPreview = document.getElementById("selectionPreview");
  const projectInfo = document.getElementById("projectInfo");

  if (selectionPreview) {
    selectionPreview.innerHTML =
      html + (projectInfo ? projectInfo.outerHTML : "");
  }
}

/**
 * Handle department change for Department Leaders
 * If they select a department other than their own, lock team and session dropdowns
 */
function onDepartmentChange() {
  var deptDropdown = document.getElementById("departmentDropdown");
  var teamDropdown = document.getElementById("teamDropdown");
  var sessionDropdown = document.getElementById("sessionDropdown");
  var selectedDept = deptDropdown.value;
  var userDept = deptDropdown.dataset.userDepartment;

  if (selectedDept !== userDept) {
    teamDropdown.value = "all";
    teamDropdown.disabled = true;
    sessionDropdown.value = "all";
    sessionDropdown.disabled = true;
  } else {
    teamDropdown.disabled = false;
    sessionDropdown.disabled = false;
  }
  updatePreview();
}

/**
 * Initialize Chart.js charts for votes and trends
 */
function initializeCharts() {
  // Vote Bar Chart
  if (
    document.getElementById("voteBarChart") &&
    document.getElementById("stats-data")
  ) {
    initVoteBarChart();
  }

  // Trend Bar Chart
  if (
    document.getElementById("trendBarChart") &&
    document.getElementById("trend-stats-data")
  ) {
    initTrendBarChart();
  }
}

/**
 * Initialize the vote distribution bar chart
 */
function initVoteBarChart() {
  try {
    const statsData = JSON.parse(
      document.getElementById("stats-data").textContent
    );
    const voteLabels = statsData.map((s) => {
      if (s.vote === "green") return "Green";
      if (s.vote === "amber") return "Amber";
      if (s.vote === "red") return "Red";
      return "No Vote";
    });

    const voteCounts = statsData.map((s) => s.count);
    const voteColors = voteLabels.map((label) => {
      if (label === "Green") return "#18b86d";
      if (label === "Amber") return "#ffc400";
      if (label === "Red") return "#e14242";
      return "#868b98";
    });

    const voteBarCtx = document.getElementById("voteBarChart").getContext("2d");
    new Chart(voteBarCtx, {
      type: "bar",
      data: {
        labels: voteLabels,
        datasets: [
          {
            label: "Votes",
            data: voteCounts,
            backgroundColor: voteColors,
          },
        ],
      },
      options: {
        responsive: false,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            ticks: { font: { size: 13 }, maxRotation: 0, minRotation: 0 },
          },
          y: {
            beginAtZero: true,
            stepSize: 1,
            ticks: { font: { size: 16 } },
          },
        },
      },
    });
  } catch (error) {
    console.error("Error initializing vote chart:", error);
  }
}

/**
 * Initialize the trend distribution bar chart
 */
function initTrendBarChart() {
  try {
    const trendData = JSON.parse(
      document.getElementById("trend-stats-data").textContent
    );
    // Guarantee all 3 categories appear, even if 0
    const trendMap = { improving: 0, steady: 0, worsening: 0 };
    trendData.forEach((t) => {
      trendMap[t.trend] = t.count;
    });

    const trendLabels = ["Improving", "About the Same", "Getting Worse"];
    const trendCounts = [
      trendMap.improving || 0,
      trendMap.steady || 0,
      trendMap.worsening || 0,
    ];

    const trendColors = ["#18b86d", "#ffc400", "#e14242"];

    const trendBarCtx = document
      .getElementById("trendBarChart")
      .getContext("2d");
    new Chart(trendBarCtx, {
      type: "bar",
      data: {
        labels: trendLabels,
        datasets: [
          {
            label: "Trend Count",
            data: trendCounts,
            backgroundColor: trendColors,
          },
        ],
      },
      options: {
        responsive: false,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            ticks: { font: { size: 13 }, maxRotation: 0, minRotation: 0 },
          },
          y: {
            beginAtZero: true,
            stepSize: 1,
            ticks: { font: { size: 16 } },
          },
        },
      },
    });
  } catch (error) {
    console.error("Error initializing trend chart:", error);
  }
}

// Store AJAX URLs for easy reference
const AJAX_URLS = {
  getTeams: "/accounts/ajax/get-teams/",
  getSessions: "/accounts/ajax/get-sessions/",
  getProject: "/accounts/ajax/get-project/",
};
