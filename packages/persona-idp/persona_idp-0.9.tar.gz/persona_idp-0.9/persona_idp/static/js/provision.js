/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */
/*
 * Borrowed from gmail.login.persona.org
 *
 * TODO: Might be easier to use jQuery??
 */

(function() {
  "use strict";

  function xhr(type, url, contentType, callback, data, csrf) {
    var req;

    function stateChange() {
      try {
        if (req.readyState === 4) {
          callback(req.responseText, req.status);
        }
      }catch(e) {}
    }

    function getRequest() {
      if (window.ActiveXObject) {
        return new window.ActiveXObject('Microsoft.XMLHTTP');
      } else if (window.XMLHttpRequest) {
        return new XMLHttpRequest();
      }
      return false;
    }

    req = getRequest();
    if(req) {
      req.onreadystatechange = stateChange;

      req.open(type, url, true);
      req.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
      if (csrf) {
        req.setRequestHeader('X-CSRF-Token', csrf);
      }

      if (data) {
        req.setRequestHeader('Content-type', contentType);
      }

      req.setRequestHeader('Accept', 'application/json;text/plain');
      req.setRequestHeader('Connection', 'close');

      req.send(data || null);
    }
  }

  function request(options) {
    xhr(options.method, options.url, "application/json",
        function(responseText, status) {
        if (status >= 200 && status < 300) {
          var respData = responseText;
          try {
            respData = JSON.parse(respData);
          } catch (ohWell) {}

          options.success(respData);
        } else {
          options.error({ status: status, responseText: responseText });
        }
      }, JSON.stringify(options.data), options.csrf);
  }

  function GET(options) {
    options.method = 'GET';
    request(options);
  }

  function POST(options) {
    options.method = 'POST';
    request(options);
  }

  function withProvenEmail(email, callback) {
    var nonce = localStorage.getItem('DPaW-Persona');
    if (!nonce) {
          navigator.id.raiseProvisioningFailure('no nonce');
    }
			
    //GET({
    POST({
      url: "/persona/session/",
      data: nonce,
      success: function(r) {
        if (true || r.proven === email) {
          //callback(r.csrf);
          callback('abc');
        } else {
          navigator.id.raiseProvisioningFailure(r);
        }
      },
      error: function(r) {
        navigator.id.raiseProvisioningFailure(r);
      }
    });
  }

  navigator.id.beginProvisioning(function (email, duration) {
    // user has an active 'session' for this email
    withProvenEmail(email, function(csrf) {
      navigator.id.genKeyPair(function(pubkey) {
        POST({
          url: '/persona/certify/',
          data: {
            pubkey: pubkey,
            duration: duration,
            email: email
          },
          csrf: csrf,
          success: function(r) {
            // all done!  woo!
            navigator.id.registerCertificate(r.cert);
          },
          error: function(r) {
            navigator.id.raiseProvisioningFailure(r);
          }
        });
      });
    });
  });

})();

