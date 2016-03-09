var token = null;

function setup() {
    token = localStorage.getItem("token");
    if (token !== null) {
        console.log('already signed in');
        console.log(token);
    }
    console.log('setup');
}

function onSignupClick() {
    console.log('signup');
    //$("#sign-up-form").validate();
}

function onSigninClick() {
    console.log('signin');
}
