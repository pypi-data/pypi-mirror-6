!function(a){"use strict";a(document).ready(function(){var a=document.createElement("script");a.setAttribute("type","text/javascript"),a.setAttribute("src","/++resource++mockup/js/config.js"),a.onload=function(){requirejs.config({baseUrl:"++resource++mockup/"}),require(["mockup-bundles-toolbar"])};var b=document.createElement("script");b.setAttribute("type","text/javascript"),b.setAttribute("src","/++resource++mockup/bower_components/requirejs/require.js"),b.onload=function(){document.getElementsByTagName("head")[0].appendChild(a)},document.getElementsByTagName("head")[0].appendChild(b);var c=document.createElement("style");c.setAttribute("type","text/less"),c.innerHTML="@import (less) \"/++resource++mockup/less/toolbar.less\"; @isBrowser: true; @pathPrefix: '/++resource++mockup/less/';",document.getElementsByTagName("head")[0].appendChild(c);var d=document.createElement("script");d.setAttribute("type","text/javascript"),d.setAttribute("src","/++resource++mockup/node_modules/grunt-contrib-less/node_modules/less/dist/less-1.4.1.js"),document.getElementsByTagName("head")[0].appendChild(d)})}(jQuery);