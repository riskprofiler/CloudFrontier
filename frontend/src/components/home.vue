<template>
  <div class="hero-image">
        <div class="overlay">
            <!-- NAVBAR STARTS -->
            <NavBar />
            <!-- NAVBAR ENDS -->

            <div class="landing-wrapper text-center">
                <div class="container">
                    <div class="col-md-12 col-lg-12 col-xl-12 col-sm-6">
                        <h1>Welcome to <span>Cloud Frontier</span></h1>
                        <p>A small project to monitor the internet attack surface of public cloud environments.</p>
                        <div>
                            <a href="/internetassets"><button type="button" class="btn btn-primary">Get Started</button></a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>


import NavBar from './navbar'

export default {
  name: "home",
  components: {
    NavBar
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
