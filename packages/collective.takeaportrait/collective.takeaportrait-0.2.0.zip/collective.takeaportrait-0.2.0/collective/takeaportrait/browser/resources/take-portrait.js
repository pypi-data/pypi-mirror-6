(function($) {

    var canvas = null, portrait = null, video = null, overlay = null, context = null, canvasElement = null,
        doPhotoButton = null, redoButton = null, savePhotoButton = null, closeButton = null,
        delaySlider = null,
        savedImageData = null, lineThick = 4, videoStarted = false, counterToDisplay = null,
        mediaWidth = mediaHeight = 0,
        savedImageX = 0, savedImageY = 0, savedImageWidth = 0, savedImageHeight = 0,
        _ = null,
        hasDragged = false, isDragging = false, oldMousePosition = {x: 0, y: 0}, mousePosition = {x: 0, y: 0},
        insideViewfinder = false, mouseButtonDown = false,
        viewFinderX = 0, viewFinderXOffset = 0, oldViewFinderXOffset = 0
        faceDetectionFn = null, faceDetectionAvailable = false, wholeCaptureSavedImageData = null;

    jarn.i18n.loadCatalog('collective.takeaportrait');
    _ = jarn.i18n.MessageFactory('collective.takeaportrait');

    /**
     * Wait for a specific delay in seconds, show a countdown progress, then save new photo in memory
     */
    function doPhotoAfterDelay(delay) {
        var startDelayTime = new Date().getTime() - 1;
        delay = delay * 1000;
        function timerLoop() {
            var currentDelayTime = new Date().getTime();
            var elapsedTime = currentDelayTime-startDelayTime;
            if (elapsedTime>=delay) {
                doPhotoButton.hide();
                savePhotoButton.show();
                closeButton.show();
                redoButton.show();
                delaySlider.hide();
                savedImageData = context.getImageData(
                    mediaWidth/2-savedImageWidth/2 + oldViewFinderXOffset, 0+lineThick,
                    savedImageWidth, savedImageHeight);
                counterToDisplay = null;
            } else {
                counterToDisplay = Math.floor((delay-elapsedTime) / 1000);
                setTimeout(timerLoop, 50);
            }
        }
        timerLoop();
    }
    
    /**
     * Get a whole camera capture, send it to the server-side face detection view,
     * then center the view finder onto the face
     */
    function faceDetection() {
        var tmpCanvas = $('<canvas width="' + wholeCaptureSavedImageData.width + 
                '" height="' + wholeCaptureSavedImageData.height + '""></canvas>').get(0);
        var tmpContext = tmpCanvas.getContext('2d');
        tmpContext.putImageData(wholeCaptureSavedImageData, 0, 0);
        $.ajax(portal_url + "/@@face-detection", {
            type: 'POST',
            dataType: 'json',
            data: {image: tmpCanvas.toDataURL('image/jpeg', 1.0)},
            success: function(data) {
                if (!hasDragged && data && data.position && data.position.length>0) {
                    if (window.console && window.console.info) {
                        window.console.info("Face detected at " + data.position);
                    };
                    var fx1 = data.position[0], fy1 = data.position[1],
                        fx2 = data.position[2], fy2 = data.position[3],
                        newMid = fx1 + ((fx2 - fx1) / 2);
                    // Let's change the viewfinder position
                    //viewFinderXOffset = - (canvas.width() / 2 - newMid);
                    oldViewFinderXOffset = - (canvas.width() / 2 - newMid);
                    viewFinderXOffset = 0;

                }
                faceDetectionFn = window.setTimeout(faceDetection, 5000);
            }
        });
    }
    
    /**
     * Initial procedure for storing a new photo in memory
     */
    function doPhoto(event) {
        event.preventDefault();
        clearTimeout(faceDetectionFn);
        var delay = parseInt(delaySlider.val(), 10);
        doPhotoAfterDelay(delay);
    }

    /**
     * Draw guides lines for photo capture
     */
    function drawViewfinder() {
        savedImageHeight = canvas.height() - 2 * lineThick;
        savedImageWidth = parseInt(savedImageHeight*75/100);
        savedImageX = mediaWidth/2-savedImageWidth/2;
        savedImageY = 0 + lineThick;
        if (!isDragging) {
            context.globalAlpha = 0.3;
        }
        // Saving the whole, clean image 
        wholeCaptureSavedImageData = context.getImageData(0, 0, mediaWidth, mediaHeight);
        context.beginPath();
        context.lineWidth = lineThick;
        context.strokeStyle = '#FFFF80';
        viewFinderX = mediaWidth/2-savedImageWidth/2 + oldViewFinderXOffset + viewFinderXOffset;
        context.moveTo(viewFinderX - lineThick/2, 0);
        context.lineTo(viewFinderX - lineThick/2, savedImageHeight+lineThick*3/2);
        context.lineTo(viewFinderX + savedImageWidth, savedImageHeight+lineThick*3/2);
        context.lineTo(viewFinderX + savedImageWidth, lineThick/2);
        context.lineTo(viewFinderX - lineThick/2, lineThick/2);
        context.stroke();
        context.globalAlpha = 1.0;
    }

    function getMousePos(event) {
        var rect = canvasElement.getBoundingClientRect();
        return {
            x: event.clientX - rect.left,
            y: event.clientY - rect.top
        };
    }

    function setCursorStyle(event) {
        if (insideViewfinder) {
            canvas.css('cursor', "ew-resize");
        } else {
            canvas.css('cursor', "default");
        }
    }

    function mouseMoving(event) {
        mousePosition = getMousePos(event)
        insideViewfinder = mousePosition.x > viewFinderX && mousePosition.x < viewFinderX + savedImageWidth;
        if (!insideViewfinder && mouseButtonDown) {
            mouseUp(event);
        }
        setCursorStyle(event);
        isDragging = insideViewfinder && mouseButtonDown; 
        if (isDragging) {
            hasDragged = true;
            viewFinderXOffset = mousePosition.x - oldMousePosition.x;
        }
    }
    
    function mouseDown(event) {
        if (event.which===1) {
            mouseButtonDown = true;
            oldMousePosition = getMousePos(event);
        }
    }
    
    function mouseUp(event) {
        mouseButtonDown = false;
        oldViewFinderXOffset = oldViewFinderXOffset + viewFinderXOffset;
        viewFinderXOffset = 0;
        isDragging = false;
    }

    function startVideo() {
        if (videoStarted) {
            // video already inited
            overlay.overlay().load();
            return;
        }
        navigator.getUserMedia(
            {video: true, audio: false},
            function(userMedia) {
                videoStarted = true;
                overlay.overlay().load();
                var videoElement = video.get(0);
                var firstRun = true;
                canvas.show();
                canvas.mousemove(mouseMoving)
                    .mousedown(mouseDown)
                    .mouseup(mouseUp);
                window.URL = window.URL || window.webkitURL || window.mozURL || window.msURL;
                video.attr('src', window.URL.createObjectURL(userMedia));

                video.bind('canplay', function(event) {
                    overlay.find('img').show();
                    function videoLoop() {
                        window.setTimeout(videoLoop, 20);
                        // test below seems weird, but anything else worked
                        if (videoElement.videoWidth>0) {
                            if (firstRun && faceDetectionAvailable) {
                                faceDetectionFn = window.setTimeout(faceDetection, 3000);
                            }
                            context.drawImage(videoElement, 0, 0, mediaWidth, mediaHeight);
                            drawViewfinder();
                            // A counter is running
                            if (counterToDisplay!==null) {
                                context.globalAlpha = 0.5;
                                context.fillStyle = "#FFFF80";
                                context.fillText(counterToDisplay + 1, 20, 80);
                                context.globalAlpha = 1.0;
                            }
                            // An image in memory: display it
                            if (savedImageData !== null) {
                                context.putImageData(
                                    savedImageData, savedImageX + oldViewFinderXOffset + viewFinderXOffset,
                                    savedImageY);
                            }
                            firstRun = false;
                        }
                    }
                    doPhotoButton.show();
                    delaySlider.show();
                    closeButton.show();
                    videoElement.play();
                    videoLoop();
                });
               
            },
            function(error) {
                overlay.overlay().close();
                if (window.console && window.console.error) {
                    window.console.error("Can't init video:" + error.code);
                }
            });
        // test server side face detection feature
        $.get(portal_url + '/@@face-detection', {'check_available': true}, function(data) {
            faceDetectionAvailable = data.enabled;
        }, 'json' );
    }
    
    /**
     * Perform an AJAX request to the server for storing image
     */
    function updatePortrait(event) {
        event.preventDefault();
        var tmpCanvas = $('<canvas width="' + savedImageData.width + 
                '" height="' + savedImageData.height + '""></canvas>').get(0);
        var context = tmpCanvas.getContext('2d');
        context.putImageData(savedImageData, 0, 0);

        $.ajax(portal_url + "/@@update-my-portrait", {
            type: 'POST',
            dataType: 'text',
            data: {image: tmpCanvas.toDataURL('image/jpeg', 1.0)},
            success: function(data, jqXHR, textStatus) {
                if (data) {
                    if (portrait.attr('src').indexOf('/defaultUser.png')>-1) {
                        portrait.attr('src', portal_url + '/portal_memberdata/portraits/' + data);
                    } else{
                        var newPortrait = portrait.clone();
                        portrait.hide();
                        newPortrait.attr('src', portrait.attr('src') + '?timestamp=' + new Date().getTime());
                        portrait.after(newPortrait).remove();
                        portrait = newPortrait;                        
                    }
                    redoButton.click();
                    overlay.overlay().close();
                }
            }
        })
    }
    
    function init() {
        // new help text
        var defaultUploadField = $('#form\\.portrait');
        var forHelpText = defaultUploadField.parent().prev('.formHelp');
        if (forHelpText.length>0) {
            var translation = _('additional_help_text');
            translation = translation ==='additional_help_text' ?
                'Alternatively you can take a photo using your webcam by clicking the "Take a photo" button.' :
                translation;
            forHelpText.html(forHelpText.html() + '<br />' + translation);
        }

        // old portrait img
        portrait = $('label[for=form\\.portrait]').nextAll('img');
        
        // canvas
        mediaWidth = overlay.width();
        mediaHeight = overlay.height()
        canvas = $('<canvas id="form.newphoto" width="' + mediaWidth +
                '" height="' + parseInt(mediaHeight/100*90) + '"></canvas>');
        canvas.prependTo(overlay);
        canvasElement = canvas.get(0);
        context = canvasElement.getContext('2d');
        context.font = "50px serif";

        // video
        video = $('<video id="form.video"></video>');
        video.hide().insertAfter(canvas);
        
        // new button
        var newFieldContainer = $('<div class="widget"></div>')
        defaultUploadField.parent().after(newFieldContainer);
        newFieldContainer.append('<input type="button" id="form.takephoto" value="' +
                                 _('Take a photo') + '"/>');
        
        return $('#form\\.takephoto');
    }
    
    $(document).ready(function() {
        
        navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia ||
                navigator.mozGetUserMedia || navigator.msGetUserMedia;

        var labelShot = _('Please, smile!');
        var labelRedo = _('Discard and redo');
        var labelSave = _('OK, I like this. Save!');
        var labelClose = _('Cancel');

        overlay = $('<div id="newPortrait" style="display:none">' +
                '<div style="text-align:center;">' +
                '<input  style="display:none" type="range" id="delay" name="delay" min="0" max="10" value="3">' +
                '</div>' +
                '<div style="text-align:center;">' +
                '<button id="shot" title="' + labelShot + '" style="display:none">' + 
                '<img alt="' + labelShot + '" src="' + portal_url + '/++resource++collective.takeaportrait.resources/web_camera.png" />' +
                '</button>' +
                '<button id="redoPhoto" title="' + labelRedo + '" style="display:none">' + 
                '<img alt="' + labelRedo + '" src="' + portal_url + '/++resource++collective.takeaportrait.resources/repeat.png" />' +
                '</button>' +
                '<button id="savePhoto" title="' + labelSave + '" style="display:none">' + 
                '<img alt="' + labelSave + '" src="' + portal_url + '/++resource++collective.takeaportrait.resources/ok.png" />' +
                '</button>' +
                '<button id="closeOverlay" title="' + labelClose + '" style="display:none">' + 
                '<img alt="' + labelClose + '" src="' + portal_url + '/++resource++collective.takeaportrait.resources/close.png" />' +
                '</button>' +
                '</div>' +
                '</div>').appendTo($('body'));

        doPhotoButton = $('#shot');
        redoButton = $('#redoPhoto');
        savePhotoButton = $('#savePhoto');
        closeButton = $('#closeOverlay');
        delaySlider = $('#delay');
        
        doPhotoButton.click(doPhoto);
        redoButton.click(function(event) {
            event.preventDefault();
            redoButton.hide();
            savePhotoButton.hide();
            doPhotoButton.show();
            delaySlider.show();
            closeButton.show();
            savedImageData = null;
        })
        savePhotoButton.click(updatePortrait);
        closeButton.click(function(event) {
            event.preventDefault();
            overlay.overlay().close();
            redoButton.click();
        });
                
        overlay.css('width', parseInt($(document).width()/100*90)+'px');
        overlay.css('height', parseInt($( window ).height()/100*90)+'px');
        
        if ($('.template-personal-information #form\\.portrait').length>0 &&
                !!(navigator.getUserMedia) && Modernizr.canvas) {
            
            var button = init();
            if (button.length==0) {
                // something goes wrong
                return
            }
            button.click(function(event) {
               event.preventDefault();
               $('#newPortrait').overlay({
                    fixed: true,
                    top: 30,
                    mask: {loadSpeed: 200, opacity: 0.9},
                    closeOnClick: false
               });
               startVideo();
            });

        }
    });
})(jQuery);
