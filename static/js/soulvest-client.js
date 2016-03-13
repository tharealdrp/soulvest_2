var token = null;
var useremail = null;

function setup() {
    // configure toastr
    toastr.options = {
        "positionClass": "toast-top-center"
    }

    token = localStorage.getItem("token");
    useremail = localStorage.getItem("useremail");
    configureMenuButtons();
}

function configureMenuButtons() {
    $('#sign-up-menu-button').removeClass('hidden');
    $('#sign-in-menu-button').removeClass('hidden');
    $('#sign-out-menu-button').addClass('hidden');
    $('#welcome-menu-button').addClass('hidden');
    if(token !== null) {
        $('#sign-up-menu-button').addClass('hidden');
        $('#sign-in-menu-button').addClass('hidden');
        $('#sign-out-menu-button').removeClass('hidden');
        $('#welcome-menu-button').removeClass('hidden');
        $('#welcome-menu-button').html("<a href='account.html'>" + useremail + "</a>");
    }
}

// do this when we click the sign out button
function onSignOutClick() {
    if(token !== null) {
        $.ajax({
            url:'api/v1/signout/',
            type:'GET',
            headers: {
                'Authorization': token
            },
            success: function(data){
                console.log(data)
                console.log('sign out success');
                window.location.href = '/';
            }
        });
    }
    localStorage.removeItem("token");
    localStorage.removeItem("useremail");
    token = null
    useremail = null
}

function credentialsError(message) {
    toastr.error(message);

    console.log("credentials error");
    var validator = $("#sign-in-form").validate();
    validator.showErrors({
        "sign-in-email": message,
        "sign-in-password": message
    });
}

// do this when we click the sign in button
function onSignInClick() {
    if (!$("#sign-in-form").valid()) {
        return;
    }

    var email = $("#sign-in-email").val();
    var password = $("#sign-in-password").val();
    console.log(JSON.stringify({
        email: email,
        password: password,
    }))
    $.ajax({
        url:'api/v1/signin/',
        type:'POST',
        data:JSON.stringify({
            email: email,
            password: password,
        }),
        contentType:"application/json; charset=utf-8",
        dataType:"json",
        success: function(data){
            console.log(data)
            console.log('sign in success');
            token = data.token;
            useremail = data.email;
            console.log(data);
            localStorage.setItem("token", token);
            localStorage.setItem("useremail", email);
            window.location.href = '/account.html';
        },
        error : function(data) {
            var responseObj = JSON.parse(data.responseText)
            console.log(responseObj.message);
            if (responseObj.message) {
                credentialsError(responseObj.message)
            }
        }
    });
}

function getAccountInfo() {
    // get account info
    $.ajax({
        url:'api/v1/account_info/',
        type:'GET',
        headers: {
            'Authorization': token
        },
        success: function(data){
            console.log("-----");
            console.log(data);
            var str = "<p>PLAID PUBLIC TOKEN:</p><p>" + data.plaid_token + "</p>";
            str += "<p>PLAID METADATA:</p><p>" + data.plaid_meta + "</p>";
            var accountInfo = JSON.parse(data.plaid_account_info);
            str += "<p>ACCOUNTS:</p>";
            for(var a in accountInfo.accounts) {
                str += "<p>" + JSON.stringify(accountInfo.accounts[a]) + "</p>";
            }
            $("#account-info").html(str);
            var plaid_meta = JSON.parse(data.plaid_meta);
            str = "<span>YOU ARE CONNECTED TO: " + plaid_meta.institution.name + "&nbsp;&nbsp;</span>";
            str += '<span class="glyphicon glyphicon-pencil pull-right" aria-hidden="true"></span>';
            $("#plaidLinkButton").html(str);
        }
    });

}

function linkAccountWithSoulvest(plaid_token, plaid_meta) {
    $.ajax({
        url:'api/v1/account_info/',
        type:'POST',
        headers: {
            'Authorization': token
        },
        data:JSON.stringify({
            plaid_token: plaid_token,
            plaid_meta: plaid_meta,
        }),
        contentType:"application/json; charset=utf-8",
        dataType:"json",
        success: function(data){
            console.log(data)
            console.log('linked account success');
            getAccountInfo();
        }
    });
}

$(document).ajaxError(function(e, xhr, settings, exception) {
    var show_debug_info = true;
    if( show_debug_info ) {
        console.log(xhr.responseText);
        $('#api-error-panel').html(xhr.responseText);
    }
});

