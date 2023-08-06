cw.mediaplayer = new Namespace('cw.mediaplayer');

$.extend(cw.mediaplayer, {
    initAudioPlayer: function (divid, cssa, mp3Url, ogaUrl) {
        var myPlayer = $("#" + divid),
            myPlayerData,
	    ignore_timeupdate, // Flag used with fixFlash_mp4
            options = {
                ready: function (event) {
                    // Hide the volume slider on mobile browsers. ie., They have no effect.
                    if(event.jPlayer.status.noVolume) {
                        // Add a class and then CSS rules deal with it.
                        $(".jp-gui").addClass("jp-no-volume");
                    }
                    $(this).jPlayer("setMedia", {
                        mp3: mp3Url,
                        oga: ogaUrl
	            });
	        },
                timeupdate: function(event) {
		    if(!ignore_timeupdate) {
		        myControl.progress.slider("value", event.jPlayer.status.currentPercentAbsolute);
		    }
	        },
	        volumechange: function(event) {
		    if(event.jPlayer.options.muted) {
		        myControl.volume.slider("value", 0);
		    } else {
		        myControl.volume.slider("value", event.jPlayer.options.volume);
		    }
	        },
	        swfPath: "js",
	        supplied: "mp3, oga",
                cssSelectorAncestor: "#" + cssa,
	        wmode: "window",
	        smoothPlayBar: true,
                preload: "auto",
	        keyEnabled: true,
                solution: "html,flash"
            };
        var myControl = {
	    progress: $(options.cssSelectorAncestor + " .jp-progress-slider"),
	    volume: $(options.cssSelectorAncestor + " .jp-volume-slider")
	};
        // Instance jPlayer
	myPlayer.jPlayer(options);

	// A pointer to the jPlayer data object
	myPlayerData = myPlayer.data("jPlayer");

	// Define hover states of the buttons
	$('.jp-gui ul li').hover(
	    function() { $(this).addClass('ui-state-hover'); },
	    function() { $(this).removeClass('ui-state-hover'); }
	);

	// Create the progress slider control
	myControl.progress.slider({
	    animate: "fast",
	    max: 100,
	    range: "min",
	    step: 0.1,
	    value : 0,
	    slide: function(event, ui) {
		var sp = myPlayerData.status.seekPercent;
		if(sp > 0) {
		    // Apply a fix to mp4 formats when the Flash is used.
		    if(fixFlash_mp4) {
			ignore_timeupdate = true;
			clearTimeout(fixFlash_mp4_id);
			fixFlash_mp4_id = setTimeout(function() {
			    ignore_timeupdate = false;
			},1000);
		    }
		    // Move the play-head to the value and factor in the seek percent.
		    myPlayer.jPlayer("playHead", ui.value * (100 / sp));
		} else {
		    // Create a timeout to reset this slider to zero.
		    setTimeout(function() {
			myControl.progress.slider("value", 0);
		    }, 0);
		}
	    }
	});

        // Create the volume slider control
        myControl.volume.slider({
	    animate: "fast",
	    max: 1,
	    range: "min",
	    step: 0.01,
	    value : $.jPlayer.prototype.options.volume,
	    slide: function(event, ui) {
	        myPlayer.jPlayer("option", "muted", false);
	        myPlayer.jPlayer("option", "volume", ui.value);
	    }
        });
    },

    initPlaylist: function(divid, cssSelector, playlist, customSettings) {
        var jplayerSettings = {
            swfPath: "js",
	    supplied: "", // should be overridden by customSettings
	    wmode: "window",
	    smoothPlayBar: true,
            preload: "auto",
	    keyEnabled: true,
            playlistOptions: {
                enableRemoveControls: true
            }
        };
        $.extend(jplayerSettings, customSettings);
        var player = new jPlayerPlaylist(
            {
                jPlayer: "#" + divid,
	        cssSelectorAncestor: "#"+ cssSelector
            },
            playlist,
            jplayerSettings);
    }
});
