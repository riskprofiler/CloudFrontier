<template>
  <!-- Changing github handle to shivamethicalhat -->
  <div>
    <div style="position: relative;">
      <NavbarDashboard />
      <div class="tab-content">
        <div class="tab-pane active" id="dashboard">
          <div id="map"></div>

          <div class="content">
            <div class="container">
              <div class="col-md-12 col-sm-12 col-lg-12 col-xl-12">
                <h4 class="main-heading">Dashboard</h4>
                <p class="para">
                  Displays the data of most commonly used ports, administrative services, vulnerabilities
                  and aggregated count on the number of assets being monitored by CloudFrontier
                </p>
              </div>

              <div class="col-md-12 col-sm-12 col-lg-12 col-xl-12">
                <div class="row">
                  <div class="col-md-4 col-sm-6 col-xl-4 col-lg-4 text-center">
                    <div class="dashboard-boxes mbsmall20 bg-black">
                      <div class="left">
                        <div class="icon">
                          <i class="fas fa-project-diagram"></i>
                        </div>
                      </div>

                      <div class="right">
                        <h5 class="total-no">{{count.open_ports}}</h5>
                        <div class="name">Ports</div>
                      </div>
                    </div>
                  </div>

                  <div class="col-md-4 col-sm-6 col-xl-4 col-lg-4 text-center">
                    <div class="dashboard-boxes mbsmall20 bg-black">
                      <div class="left">
                        <div class="icon">
                          <i class="fas fa-map-marker-alt"></i>
                        </div>
                      </div>

                      <div class="right">
                        <h5 class="total-no">{{count.ip_address}}</h5>
                        <div class="name">IPs</div>
                      </div>
                    </div>
                  </div>

                  <!-- <div class="col-md-3 col-sm-6 col-xl-3 col-lg-3 text-center">
                    <div class="dashboard-boxes mbsmall20 bg-black">
                      <div class="left">
                        <div class="icon">
                          <i class="fas fa-server"></i>
                        </div>
                      </div>

                      <div class="right">
                        <h5 class="total-no">{{count.services}}</h5>
                        <div class="name">Services</div>
                      </div>
                    </div>
                  </div>-->

                  <div class="col-md-4 col-sm-6 col-xl-4 col-lg-4 text-center">
                    <div class="dashboard-boxes bg-black">
                      <div class="left">
                        <div class="icon">
                          <i class="fas fa-exclamation"></i>
                        </div>
                      </div>

                      <div class="right">
                        <h5 class="total-no">{{count.vuln}}</h5>
                        <div class="name">Vulnerabilities</div>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="row" style="margin-top: 50px;">
                  <div class="col-md-4 col-sm-12 col-xl-4 col-lg-4">
                    <div class="dashboard-wrapper mbsmall20 bg-black">
                      <div class="heading common-ports">
                        <span>
                          <i class="fas fa-circle" aria-hidden="true"></i>
                        </span>
                        Most Commonly used ports
                      </div>
                      <div class="inner-section">
                        <nw-loader v-if="commanPortsLoaded === null"></nw-loader>
                        <center v-if="(commanPorts.length === 0 && commanPortsLoaded === false)"><h5>No data found</h5></center>
                        <table v-if="(commanPorts.length > 0  && commanPortsLoaded === true)" class="table dashboard-table">
                          <thead>
                            <tr>
                              <th>Ports</th>
                              <th>Count</th>
                            </tr>
                          </thead>

                          <tbody>
                            <nw-dashboard-table-row
                              v-for="(item,index) in commanPorts"
                              :key="index"
                              :name="'Port '+item.name"
                              :count="item.value"
                            ></nw-dashboard-table-row>
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>

                  <div class="col-md-4 col-sm-12 col-xl-4 col-lg-4">
                    <div class="dashboard-wrapper mbsmall20 bg-black">
                      <div class="heading admin-ports">
                        <span>
                          <i class="fas fa-circle" aria-hidden="true"></i>
                        </span>
                        Administrative Ports
                      </div>
                      <div class="inner-section">
                        <nw-loader v-if="administrativePortsLoaded === null"></nw-loader>
                        <center v-if="(administrativePorts.length === 0 && administrativePortsLoaded === false)"><h5>No data found</h5></center>
                        <table v-if="(administrativePorts.length > 0 && administrativePortsLoaded === true)" class="table dashboard-table">
                          <thead>
                            <tr>
                              <th>Ports</th>
                              <th>Count</th>
                            </tr>
                          </thead>
                          <tbody>
                            <nw-dashboard-table-row
                              v-for="(item,index) in administrativePorts"
                              :key="index"
                              :name="'Port '+item.name"
                              :count="item.value"
                            ></nw-dashboard-table-row>
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>

                  <div class="col-md-4 col-sm-12 col-xl-4 col-lg-4">
                    <div class="dashboard-wrapper bg-black">
                      <div class="heading notable-ip">
                        <span>
                          <i class="fas fa-circle" aria-hidden="true"></i>
                        </span>
                        Vulnerabilities
                      </div>
                      <div class="inner-section">
                        <nw-loader v-if="vulnerabilitiesLoaded === null"></nw-loader>
                        <center v-if="(vulnerabilities.length === 0 && vulnerabilitiesLoaded === false)"><h5>No data found</h5></center>
                        <table v-if="vulnerabilities.length > 0 && vulnerabilitiesLoaded === true" class="table dashboard-table">
                          <thead>
                            <tr>
                              <th>CVE Name</th>
                              <th>Count</th>
                            </tr>
                          </thead>
                          <tbody>
                            <nw-dashboard-table-row
                              v-for="(item,index) in vulnerabilities"
                              :key="index"
                              :name="item.name"
                              :count="item.value"
                            ></nw-dashboard-table-row>
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="tab-pane container fade" id="internet_asset">
          <div class="content">
            <div class="col-md-12 col-sm-12 col-lg-12 col-xl-12">
              <h4 class="main-heading">Internet Assets</h4>
              <p class="para">
                Internet Attack Surface view of organizations multiple public cloud providers
              </p>
            </div>

            <div class="col-md-12 col-sm-12 col-lg-12 col-xl-12">
              <div class="row">
                <div class="col-md-12 col-lg-12 col-xl-12 col-sm-6">
                  <ul class="nav nav-pills asset-nav-pills">
                    <li class="nav-item">
                      <a
                        class="nav-link active mb0 bg-black"
                        data-toggle="pill"
                        @click="loadDate('ip_address')"
                        href="#ip_address"
                      >
                        <span class="icon">
                          <i class="fas fa-map-marked-alt"></i>
                        </span>
                        <span class="pill-name">IP Address</span>
                        <span class="total-no">({{count.ipAddress}})</span>
                      </a>
                    </li>
                    <li class="nav-item">
                      <a
                        class="nav-link bg-black"
                        data-toggle="pill"
                        @click="loadDate('domain')"
                        href="#domain"
                      >
                        <span class="icon">
                          <i class="fas fa-globe-americas"></i>
                        </span>
                        <span class="pill-name">Domain</span>
                        <span class="total-no">({{count.domain}})</span>
                      </a>
                    </li>
                    <li class="nav-item">
                      <a
                        class="nav-link bg-black mb0"
                        data-toggle="pill"
                        @click="loadDate('object_storage')"
                        href="#obj_storage"
                      >
                        <span class="icon">
                          <i class="fas fa-archive"></i>
                        </span>
                        <span class="pill-name">Object Storages</span>
                        <span class="total-no">({{count.objectStorage}})</span>
                      </a>
                    </li>
                    <li class="nav-item">
                      <a
                        class="nav-link bg-black mb0"
                        data-toggle="pill"
                        @click="loadDate('data_storage')"
                        href="#data_storage"
                      >
                        <span class="icon">
                          <i class="fas fa-server"></i>
                        </span>
                        <span class="pill-name">Data Storages</span>
                        <span class="total-no">({{count.dataStorgae}})</span>
                      </a>
                    </li>
                    <li class="nav-item">
                      <a
                        class="nav-link bg-black mb0"
                        data-toggle="pill"
                        @click="loadDate('api_endpoint')"
                        href="#api_endpoint"
                      >
                        <span class="icon">
                          <i class="fas fa-arrows-alt"></i>
                        </span>
                        <span class="pill-name">API Endpoints</span>
                        <span class="total-no">({{count.apiEndpoint}})</span>
                      </a>
                    </li>
                    <li class="nav-item">
                      <a
                        class="nav-link bg-black"
                        data-toggle="pill"
                        @click="loadDate('cdn')"
                        href="#cdn"
                      >
                        <span class="icon">
                          <i class="fas fa-network-wired"></i>
                        </span>
                        <span class="pill-name">CDN</span>
                        <span class="total-no">({{count.cdn}})</span>
                      </a>
                    </li>
                  </ul>
                </div>

                <div class="col-md-12 col-lg-12 col-xl-12 col-sm-6">
                  <div class="tab-content">
                    <div class="tab-pane container active" id="ip_address">
                      <table class="table table-striped asset-table bg-black">
                        <thead>
                          <tr>
                            <th>IP Address</th>
                            <th>ASN</th>
                            <th>Location</th>
                            <th>Virustotal Score</th>
                            <th>Cloud Provider</th>
                            <th>Ports</th>
                            <th>Vulnerabilities</th>
                          </tr>
                        </thead>
                        <tbody>
                          <nw-ip-address-row
                            v-for="(item,index) in ipAddress"
                            :key="index"
                            :sk="item.sk"
                            :countryCode="item.country_code"
                            :provider="item.provider"
                            :asn="item.asn"
                            :ports="item.ports"
                            :vtScor="item.vt_score"
                            :vulns="item.vulns"
                          ></nw-ip-address-row>
                        </tbody>
                      </table>
                    </div>

                    <div class="tab-pane container fade" id="domain">
                      <table class="table table-striped asset-table bg-black">
                        <thead>
                          <tr>
                            <th>Domain Name</th>
                            <th>Virustotal</th>
                            <th>Mozilla Observatory</th>
                            <th>Cloud Provider</th>
                          </tr>
                        </thead>
                        <tbody>
                          <nw-domain-row
                            v-for="(item,index) in domain"
                            :key="index"
                            :vtScor="item.vt_score"
                            :domainName="item.sk"
                            :observatoryGrade="item.observatory_grade"
                            :provider="item.provider"
                          ></nw-domain-row>
                        </tbody>
                      </table>
                    </div>

                    <div class="tab-pane container fade" id="obj_storage">
                      <table class="table table-striped asset-table bg-black">
                        <thead>
                          <tr>
                            <th>Storage Name</th>
                            <th>Cloud Provider</th>
                            <th style="width: 12%; text-align: center;">Private Indicator</th>
                          </tr>
                        </thead>
                        <tbody>
                          <nw-object-storage-row
                            v-for="(item,index) in objectStorage"
                            :key="index"
                            :storageName="item.sk"
                            :provider="item.provider"
                            :publicIndicator="item.is_public"
                          ></nw-object-storage-row>
                        </tbody>
                      </table>
                    </div>

                    <div class="tab-pane container fade" id="data_storage">
                      <table class="table table-striped asset-table bg-black">
                        <thead>
                          <tr>
                            <th>Connection Endpoint</th>
                            <th>Storage Type</th>
                            <th>Cloud Provider</th>
                            <th style="width: 12%; text-align: center;">Private Indicator</th>
                          </tr>
                        </thead>
                        <tbody>
                          <nw-data-storage-row
                            v-for="(item,index) in dataStorgae"
                            :key="index"
                            :connectionEndpoint="item.sk"
                            :storageType="item.storage_type"
                            :provider="item.provider"
                            :publicIndicator="item.is_public"
                          ></nw-data-storage-row>
                        </tbody>
                      </table>
                    </div>

                    <div class="tab-pane container fade" id="api_endpoint">
                      <table class="table table-striped asset-table bg-black">
                        <thead>
                          <tr>
                            <th>URL Endpoint</th>
                            <th>Cloud Provider</th>
                            <th style="width: 12%; text-align: center;">Private Indicator</th>
                          </tr>
                        </thead>
                        <tbody>
                          <nw-api-endpoints-row
                            v-for="(item,index) in apiEndpoint"
                            :key="index"
                            :name="item.name"
                            :urlEndpoint="item.sk"
                            :provider="item.provider"
                            :publicIndicator="item.is_public"
                          ></nw-api-endpoints-row>
                        </tbody>
                      </table>
                    </div>

                    <div class="tab-pane container fade" id="cdn">
                      <table class="table table-striped asset-table bg-black">
                        <thead>
                          <tr>
                            <th>Name</th>
                            <th>URL Endpoint</th>
                            <th>Custom Domain</th>
                            <th>Status</th>
                            <th>Cloud Provider</th>
                          </tr>
                        </thead>

                        <tbody>
                          <nw-cdn-row
                            v-for="(item,index) in cdn"
                            :key="index"
                            :name="item.name"
                            :urlEndpoint="item.sk"
                            :customeDomain="item.custom_domain"
                            :status="item.status"
                            :provider="item.provider"
                          ></nw-cdn-row>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="!watchedBanner" class="landingOverLay" id="landingPage">
      <div class="centered-info">
        <h1>Cloud Frontier</h1>
        <p>A small project to monitor the internet attack surface of public cloud environments.</p>

        <div class="logos-wrapper">
          <div class="logo text-center">
            <div class="logo-fix-height">
              <img src="images/aws-icon.svg" />
            </div>
            <small>AWS</small>
          </div>

          <div class="logo text-center">
            <div class="logo-fix-height">
              <img src="images/azure-icon.svg" />
            </div>
            <small>Azure</small>
          </div>

          <div class="logo text-center">
            <div class="logo-fix-height">
              <img src="images/oracle-icon.svg" />
            </div>
            <small>Oracle</small>
          </div>

          <div class="logo text-center">
            <div class="logo-fix-height">
              <img src="images/digitalocean-icon.svg" />
            </div>
            <small>Diital Ocean</small>
          </div>

          <div class="logo text-center">
            <div class="logo-fix-height">
              <img src="images/gcp-icon.svg" />
            </div>
            <small>GCP</small>
          </div>
        </div>
        <button @click="closeOverlay">Get Started</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import L from "leaflet";
import NavbarDashboard from "./navbar-dashboard";
import nwIpAddressRow from "./sub-components/internetAssets/ip-address-row";
import nwDomainRow from "./sub-components/internetAssets/domain-row";
import nwObjectStorgaeRow from "./sub-components/internetAssets/object-storage-row";
import nwDataStorgaeRow from "./sub-components/internetAssets/data-storage-row";
import nwApiEndpointRow from "./sub-components/internetAssets/api-endpoint.row";
import nwcdnRow from "./sub-components/internetAssets/cdn-row";
import nwDashboardTableRow from "./sub-components/internetAssets/dashboard-table-row";
import loader from "./loader";

export default {
  name: "internetassets",
  components: {
    NavbarDashboard,
    "nw-ip-address-row": nwIpAddressRow,
    "nw-domain-row": nwDomainRow,
    "nw-object-storage-row": nwObjectStorgaeRow,
    "nw-data-storage-row": nwDataStorgaeRow,
    "nw-api-endpoints-row": nwApiEndpointRow,
    "nw-cdn-row": nwcdnRow,
    "nw-dashboard-table-row": nwDashboardTableRow,
    "nw-loader": loader
  },
  data() {
    return {
      apiUrl: null,
      selected_query: "ip_address",
      ipAddress: [],
      domain: [],
      objectStorage: [],
      dataStorgae: [],
      apiEndpoint: [],
      cdn: [],
      count: {
        open_ports: 0,
        ip_address: 0,
        services: 0,
        vuln: 0,
        ipAddress: 0,
        domain: 0,
        objectStorage: 0,
        dataStorgae: 0,
        apiEndpoint: 0,
        cdn: 0
      },
      commanPorts: [],
      administrativePorts: [],
      vulnerabilities: [],
      watchedBanner: false,
      commanPortsLoaded: null,
      administrativePortsLoaded: null,
      vulnerabilitiesLoaded: null
    };
  },
  methods: {
    closeOverlay() {
      var config = {
        method: "get",
        url: this.apiUrl + "/start",
        headers: {}
      };

      axios(config)
        .then(response => {
          console.log(JSON.stringify(response.data));
          localStorage.setItem("started", true);
          document.getElementById("landingPage").style.display = "none";
        })
        .catch(function(error) {
          console.log(error);
        });
    },
    loadDashboard() {
      var dashboardCountConfig = {
        method: "get",
        url: this.apiUrl + "/dashboard/dashboard"
      };

      axios(dashboardCountConfig)
        .then(dashboardCountArr => {
          dashboardCountArr.data.data.dashboard.map(item => {
            Object.entries(item).forEach(([key, value]) => {
              if (this.count[key] < value) {
                this.count[key] = value;
              }
            });
          });
        })
        .catch(function(error) {
          console.log(error);
        });

      var adminPortConfig = {
        method: "get",
        url: this.apiUrl + "/dashboard/administrative-ports",
        headers: {}
      };

      axios(adminPortConfig)
        .then(adminport => {
          this.administrativePortsLoaded = false;
          if (adminport.data.data.admin_ports != "NA") {
            this.administrativePortsLoaded = true;
            if (
              this.administrativePorts.length <
              adminport.data.data.admin_ports.length
            ) {
              this.administrativePorts = [];
              adminport.data.data.admin_ports.map(item => {
                Object.entries(item).forEach(([key, value]) => {
                  let obj = {};
                  obj.name = key;
                  obj.value = value;
                  this.administrativePorts.push(obj);
                });
              });
            }
          }
        })
        .catch((error) => {
          console.log(error);
          this.administrativePortsLoaded = false;
        });

      var commanPortsConfig = {
        method: "get",
        url: this.apiUrl + "/dashboard/common-ports",
        headers: {}
      };

      axios(commanPortsConfig)
        .then(commanPorts => {
          this.commanPortsLoaded = false;
          if (commanPorts.data.data.common_ports != "NA") {
            this.commanPortsLoaded = true;
            if (
              this.commanPorts.length <
              commanPorts.data.data.common_ports.length
            ) {
              this.commanPorts = [];
              commanPorts.data.data.common_ports.map(item => {
                Object.entries(item).forEach(([key, value]) => {
                  let obj = {};
                  obj.name = key;
                  obj.value = value;
                  this.commanPorts.push(obj);
                });
              });
            }
          }
        })
        .catch((error) => {
          console.log(error);
          this.commanPortsLoaded = false;
        });

      var vulnerabilitiesConfig = {
        method: "get",
        url: this.apiUrl + "/dashboard/vulnerabilities",
        headers: {}
      };

      axios(vulnerabilitiesConfig)
        .then(vulnerabilities => {
          this.vulnerabilitiesLoaded = false;
          if (vulnerabilities.data.data.vulnerabilities != "NA") {
            this.vulnerabilitiesLoaded = true;
            if (
              this.vulnerabilities.length <
              vulnerabilities.data.data.vulnerabilities.length
            ) {
              this.vulnerabilities = [];
              vulnerabilities.data.data.vulnerabilities.map(item => {
                Object.entries(item).forEach(([key, value]) => {
                  let obj = {};
                  obj.name = key;
                  obj.value = value;
                  this.vulnerabilities.push(obj);
                });
              });
            }
          }
        })
        .catch((error) =>{
          console.log(error);
          this.vulnerabilitiesLoaded = false;
        });
    },
    loadDate(query) {
      var config = {
        method: "get",
        url: this.apiUrl + "/assets?asset_type=" + query
      };

      axios(config)
        .then(response => {
          // console.log(response.data.assets);
          this.updateDate(query, response.data.assets);
        })
        .catch(error => {
          console.log(error);
        });
    },
    updateDate(assetType, assets) {
      switch (assetType) {
        case "ip_address":
          if (this.ipAddress.length < assets.length) {
            this.count.ipAddress = assets.length;
            this.ipAddress = assets;
          }
          break;
        case "domain":
          if (this.domain.length < assets.length) {
            this.count.domain = assets.length;
            this.domain = assets;
          }
          break;
        case "object_storage":
          if (this.objectStorage.length < assets.length) {
            this.count.objectStorage = assets.length;
            this.objectStorage = assets;
          }
          break;
        case "data_storage":
          if (this.dataStorgae.length < assets.length) {
            this.count.dataStorgae = assets.length;
            this.dataStorgae = assets;
          }
          break;
        case "api_endpoint":
          if (this.apiEndpoint.length < assets.length) {
            this.count.apiEndpoint = assets.length;
            this.apiEndpoint = assets;
          }
          break;
        case "cdn":
          if (this.cdn.length < assets.length) {
            this.count.cdn = assets.length;
            this.cdn = assets;
          }
          break;
        default:
          console.log(assetType);
          break;
      }
    },
    loadMapData(map) {
      var config = {
        method: "get",
        url: this.apiUrl + "/dashboard/ip-geo"
      };

      axios(config)
        .then(function(response) {
          let geoIp = response.data.data.geo_ip;
          geoIp.map(geo => {
            L.marker([geo.latitude, geo.longitude])
              .addTo(map)
              .bindPopup(geo.ip_address, {
                closeButton: false
              })
              .openPopup();
          });
        })
        .catch(function(error) {
          console.log(error);
        });
    }
  },
  mounted() {
    var map = L.map("map").setView([61.524, -105.3188], 1);
    this.map = map;
    L.tileLayer(
      "https://api.maptiler.com/maps/hybrid/{z}/{x}/{y}.jpg?key=QO8LoIdDfbJdoPnNhvgI",
      {
        fullscreenControl: true,
        tileSize: 512,
        zoomOffset: -1,
        minZoom: 1,
        attribution:
          '<a href="https://www.maptiler.com/copyright/" target="_blank">© MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">© OpenStreetMap contributors</a>',
        crossOrigin: true
      }
    ).addTo(map);
    this.loadMapData(map);
  },
  created() {
    this.apiUrl = this.$config.ServiceEndpoint;
    this.watchedBanner = localStorage.getItem("started") ? true : false;
    this.loadDashboard();
    this.loadDate("ip_address");
    this.loadDate("domain");
    this.loadDate("object_storage");
    this.loadDate("data_storage");
    this.loadDate("api_endpoint");
    this.loadDate("cdn");
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#map {
  width: 100%;
  height: 200px;
}
</style>
