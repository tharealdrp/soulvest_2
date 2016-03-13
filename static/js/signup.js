// are we already signed in?
token = localStorage.getItem("token");
if (token !== null) {
    //window.location.href = '/portfolios.html'; //one level up
}

// do this when the document is loaded
$(document).ready(function(){
    showSignUpPanel();
    // sign up validation
    $('#sign-up-form').validate({
        rules: {
            'confirm-sign-up-password': {
                equalTo: '#sign-up-password'
            }
        }
    });

    jQuery.extend(jQuery.validator.messages, {
        equalTo:"Password fields do not match.",
    });

    $("select[name=bank]").change(function(){
        var bank = $(this).val();
        $(".bank").html(bank);
    });
});

// example showing how to manually add an error message
function addSignUpEmailError(message) {
    toastr.error(message);
    var validator = $("#sign-up-form").validate();
    validator.showErrors({
        "email": message
    });
}

function addSignUpPasswordError(message) {
    toastr.error(message);
    var validator = $("#sign-up-form").validate();
    validator.showErrors({
        "sign-up-password": message
    });
}

// hide show sign up / sign in panels
function hidePanels() {
    $("#sign-up-panel").hide();
    $("#sign-in-panel").hide();
    $("#select-institution-panel").hide();
    $("#connect-account-panel").hide();
    $("#select-account-panel").hide();
}

function setProgress(progress) {
    progress += "%";
    $(".progress-bar").css("width", progress);
    $(".progress-number").html(progress);
}

function showSignUpPanel() {
    hidePanels();
    $("#sign-up-panel").fadeIn('slow');
    setProgress("0");
}

function showSignInPanel() {
    hidePanels();
    $("#sign-in-panel").fadeIn('slow');
    setProgress("0");
}

function showSelectInstitutionPanel() {
    hidePanels();
    $("#select-institution-panel").fadeIn('slow');
    setProgress("10");
}

function showConnectAccountPanel() {
    hidePanels();
    $("#connect-account-panel").fadeIn('slow');
    setProgress("20");
}

function showSelectAccountPanel() {
    hidePanels();
    $("#select-account-panel").fadeIn('slow');
    setProgress("30");
    var plaidMeta = JSON.parse(localStorage.getItem("plaid_metadata"));
    console.log(plaidMeta);
    var institution = plaidMeta.institution;
    console.log(institution);
    $(".bank").html(institution.name);

}

// do this when we click the sign up button
function onSignUpClick() {
    // temporary
    //showSelectInstitutionPanel();
    //return;

    if (!$("#sign-up-form").valid()) {
        return;
    }

    var email = $("#email").val();
    var password = $("#sign-up-password").val();
    var confirm_password = $("#confirm-sign-up-password").val();
    console.log(JSON.stringify({
        email: email,
        password: password,
        confirm_password: confirm_password
    }))
    $.ajax({
        url:'api/v1/signup/',
        type:'POST',
        data:JSON.stringify({
            email: email,
            password: password,
            confirm_password: confirm_password
        }),
        contentType:"application/json; charset=utf-8",
        dataType:"json",
        success: function(data){
            console.log(data)
            console.log('signup success');
            token = data.token;
            localStorage.setItem("token", token);
            localStorage.setItem("useremail", email);
            configureMenuButtons();
            showSelectInstitutionPanel();
        },
        error : function(data) {
            var responseObj = JSON.parse(data.responseText)
            console.log(responseObj.message);
            if (responseObj.message && responseObj.message.password) {
                addSignUpPasswordError(responseObj.message.password)
            }

            if (responseObj.message && responseObj.message.email) {
                addSignUpEmailError(responseObj.message.email)
            }
        }
    });
}
