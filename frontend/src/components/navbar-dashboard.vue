<template>
  <div>
    <nav class="navbar navbar-expand-md main-navbar">
      <div class="container">
        <!-- Brand -->
        <a class="navbar-brand" href="#">
            <img src="images/logo.png">
        </a>

        <!-- Toggler/collapsibe Button -->
        <button
          class="navbar-toggler"
          type="button"
          data-toggle="collapse"
          data-target="#collapsibleNavbar"
        >
          <span class="navbar-toggler-icon"></span>
        </button>

        <!-- Navbar links -->
        <div class="collapse navbar-collapse" id="collapsibleNavbar">
          <ul class="nav nav-pills">
            <li class="nav-item">
              <a class="nav-link active" data-toggle="pill" href="#dashboard">
                <span class="icon">
                  <i class="fas fa-columns"></i>
                </span>
                <span class="pill-name">Dashboard</span>
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" data-toggle="pill" href="#internet_asset">
                <span class="icon">
                  <i class="fas fa-ethernet"></i>
                </span>
                <span class="pill-name">Internet Asset</span>
              </a>
            </li>
          </ul>

          <ul class="navbar-nav">
            <li class="nav-item">
              <a class="nav-link">
                <div class="custom-control custom-switch">
                  <input type="checkbox" class="custom-control-input" id="darkSwitch" />
                  <label class="custom-control-label" for="darkSwitch">Switch to Dark Mode</label>
                </div>
              </a>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  </div>
</template>

<script>
export default {
  name: "internetassets",
  components: {}
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
