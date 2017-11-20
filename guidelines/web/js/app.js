$(document).ready(function () {
    //Initialize tooltips
    $('.nav-tabs > li a[title]').tooltip();
    $('.col-xs-2 > a[title]').tooltip();
    
    //Wizard
    $('a[data-toggle="tab"]').on('show.bs.tab', function (e) {

        var $target = $(e.target);
    
        if ($target.parent().hasClass('disabled')) {
            return false;
        }
    });

    $(".next-step").click(function (e) {

        var $active = $('.wizard .nav-tabs li.active');
        $active.next().removeClass('disabled');
        nextTab($active);

    });
    $(".prev-step").click(function (e) {

        var $active = $('.wizard .nav-tabs li.active');
        prevTab($active);

    });
});

function nextTab(elem) {
    $(elem).next().find('a[data-toggle="tab"]').click();
}
function prevTab(elem) {
    $(elem).prev().find('a[data-toggle="tab"]').click();
}

+ function($) {
    'use strict';

    // UPLOAD CLASS DEFINITION
    // ======================

    var dropZone = document.getElementById('drop-zone');
    var uploadForm = document.getElementById('js-upload-form');

    var startUpload = function(file) {
        $("#upload-progress").show("slow");
        //var file = files[0];
        var formData = new FormData();
        formData.append("file1", file);

        $.ajax({url: 'http://localhost:8080/ws/ontology',
                method: 'POST',
                type: 'POST',
                data: formData,
                contentType: 'text/turtle',
                processData: false,
                xhr: function()
                {
                    var xhr = new window.XMLHttpRequest();
                    xhr.upload.addEventListener("progress",
                        uploadProgressHandler,
                        false
                    );
                    xhr.addEventListener("load", loadHandler, false);
                    xhr.addEventListener("error", errorHandler, false);
                    //xhr.addEventListener("abort", abortHandler, false);

                    return xhr;
                }
            }
        );

        $("#upload-info").html(file.name);
        console.log(file)
    };

    function loadHandler()
    {
        $("#upload-info").addClass("list-group-item-success");
        $("#upload-info").append("<span class='badge alert-success pull-right'>Success", "</span>");
        $(".js-upload-finished").show("slow");
    }

    function errorHandler()
    {
        $("#upload-info").addClass("list-group-item-danger");
        $("#upload-info").append("<span class='badge alert-danger pull-right'>Failed", "</span>");
        $(".js-upload-finished").show("slow");
    }


    function uploadProgressHandler(event)
    {
        //$(".progress-bar").html("Uploaded "+event.loaded+" bytes of "+event.total);
        var percent = (event.loaded / event.total) * 100;
        var progress = Math.round(percent);
        $(".progress-bar").attr('aria-value-now', progress.toString());
        $(".progress-bar").attr('style', 'width: ' + progress.toString() + '%');
        $(".sr-only").html(progress + "% Complete");
    }

    uploadForm.addEventListener('submit', function(e) {
        var uploadFile = document.getElementById('js-upload-files').files[0];
        e.preventDefault()

        startUpload(uploadFile)
    });

    dropZone.ondrop = function(e) {
        e.preventDefault();
        this.className = 'upload-drop-zone';

        startUpload(e.dataTransfer.file)
    };

    dropZone.ondragover = function() {
        this.className = 'upload-drop-zone drop';
        return false;
    };

    dropZone.ondragleave = function() {
        this.className = 'upload-drop-zone';
        return false;
    };

}(jQuery);

jQuery(function($) {
    var loadedForm;
    $.getJSON("guideline_form.json", function(loadedForm) {
        console.log(loadedForm); // this will show the info it in firebug console
        var fbTemplate = document.getElementById('fb-template');
        $('.fb-render').formRender({
          dataType: 'json',
          formData: loadedForm
        });
    });    
    
  });
