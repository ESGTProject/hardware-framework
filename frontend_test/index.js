var firebase = require("firebase");

var config = {
  apiKey: "AIzaSyAhfZI9SSNWMVcoODVovNrfLlmh28vVpvk",
  authDomain: "esgtapp.firebaseapp.com",
  databaseURL: "https://esgtapp.firebaseio.com",
  storageBucket: "esgtapp.appspot.com",
  messagingSenderId: "577511514187"
};

firebase.initializeApp(config);

firebase.auth().signInAnonymously().catch(function (error) {
  // Handle Errors here.
  var errorCode = error.code;
  var errorMessage = error.message;
});

firebase.auth().onAuthStateChanged(function (user) {
  if (user) {
    // User is signed in.
    var isAnonymous = user.isAnonymous;
    var uid = user.uid;
    console.log("Signed in anonymously!");
    // ...
  } else {
    // User is signed out.
    // ...
  }
  // ...
});

// Attach listener for device
var deviceUUID = '-KgICjJhWb4elAflr1_J';
var userUUID = '';
function startListeners() {
  var rootRef = firebase.database().ref();
  rootRef.child('devices/' + '-KgICjJhWb4elAflr1_J' + '/user_current').on('value', function (userCurrentSnapshot) {

    // Remove all listeners at previous user config path
    rootRef.child('users/' + userUUID).off();

    // Attach new listener at new user config path
    userUUID = userCurrentSnapshot.val();
    console.log('UserUUID: ' + userUUID);
    rootRef.child('users/' + userUUID).on('value', function (configSnapshot) {
      console.log('UserConfig:');
      console.log('\tdisplay_name: ' + configSnapshot.child('display_name').val());
      console.log('\tnews_source: ' + configSnapshot.child('news_source').val());
      console.log('\ttime_zone: ' + configSnapshot.child('time_zone').val());
      console.log('\tuse_imperial: ' + configSnapshot.child('use_imperial').val());
      console.log('\tusername: ' + configSnapshot.child('username').val());
      console.log('\tweather_location: ' + configSnapshot.child('weather_location').val());
    });
  });
  console.log('Started listening for changes to config...\n');
}

startListeners()