function supports_html5_storage() {
    try {
        return 'localStorage' in window && window['localStorage'] !== null;
    } catch (e) {
        return false;
    }
}

function randomString(length) {
    var text = "";
    var chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for(var i=0; i < length; i++) {
        text += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return text;
}

function register(baseUrl, username, email, password) {
    var deferred = new $.Deferred();
    if (username && email && password) {
        challenge = randomString(10)
        encrypted_challenge = sjcl.encrypt(password, challenge)
        $.when(
            $.ajax({
                type: "POST",
                url: baseUrl,
                data: {
                    "username" : username,
                    "email" : email,
                    "challenge" : challenge,
                    "encrypted_challenge" : encrypted_challenge
                }
            })
        ).done(function() {
            deferred.resolve("Registration completed");
        }).fail(function() {
            deferred.reject("Registration failed");
        });
    } else {
        deferred.reject("Invalid parameters");
    }
    return deferred.promise();
}

function login(baseUrl, username, password) {
    var deferred = new $.Deferred();
    if (username && password) {
        $.when(
            $.ajax({
                type: "GET",
                url: baseUrl + "?username=" + username,
            })
        ).then(function(data) {
            return sjcl.decrypt(password, data)
        }).then(function(challenge) {
            return $.ajax({
                type: "POST",
                url: baseUrl,
                data: {
                    "username" : username,
                    "challenge" : challenge,
                }
            })
        }).then(function(rsa_public) {
            if (supports_html5_storage()) {
                localStorage.setItem("rsa_public", rsa_public);
            }
        }).done(function(data) {
            deferred.resolve("Login completed");
        }).fail(function() {
            deferred.reject("Login failed");
        });
    } else {
        deferred.reject("Invalid parameters");
    }
    return deferred.promise();
}
