$(document).ready(function () {
    //Initialize tooltips
    //$('[data-toggle="popover"]').popover();
    $("body").popover({selector: '[data-toggle=popover]'});
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

+function ($) {
    'use strict';

    // UPLOAD CLASS DEFINITION
    // ======================

    var dropZone = document.getElementById('drop-zone');
    var uploadForm = document.getElementById('js-upload-form');

    var startUpload = function (file) {
        $("#upload-progress").show("slow");
        //var file = files[0];
        var formData = new FormData();
        formData.append("file1", file);

        $.ajax({
                url: 'http://localhost:8080/ws/ontology',
                method: 'POST',
                type: 'POST',
                data: formData,
                contentType: 'text/turtle',
                processData: false,
                xhr: function () {
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

    function loadHandler() {
        $("#upload-info").addClass("list-group-item-success");
        $("#upload-info").append("<span class='badge alert-success pull-right'>Success", "</span>");
        $(".js-upload-finished").show("slow");
    }

    function errorHandler() {
        $("#upload-info").addClass("list-group-item-danger");
        $("#upload-info").append("<span class='badge alert-danger pull-right'>Failed", "</span>");
        $(".js-upload-finished").show("slow");
    }


    function uploadProgressHandler(event) {
        //$(".progress-bar").html("Uploaded "+event.loaded+" bytes of "+event.total);
        var percent = (event.loaded / event.total) * 100;
        var progress = Math.round(percent);
        $(".progress-bar").attr('aria-value-now', progress.toString());
        $(".progress-bar").attr('style', 'width: ' + progress.toString() + '%');
        $(".sr-only").html(progress + "% Complete");
    }

    uploadForm.addEventListener('submit', function (e) {
        var uploadFile = document.getElementById('js-upload-files').files[0];
        e.preventDefault()

        startUpload(uploadFile)
    });

    dropZone.ondrop = function (e) {
        e.preventDefault();
        this.className = 'upload-drop-zone';

        startUpload(e.dataTransfer.file)
    };

    dropZone.ondragover = function () {
        this.className = 'upload-drop-zone drop';
        return false;
    };

    dropZone.ondragleave = function () {
        this.className = 'upload-drop-zone';
        return false;
    };

}(jQuery);

//the following function generates the questionnaire HTML from JSON
jQuery(function ($) {
    $.getJSON("guideline_form.json", function (loadedJson) {
        console.log(loadedJson); // debug: output json to console
        var groups = $.parseJSON(JSON.stringify(loadedJson[0]));
        $.each(groups, function (index, group) {
            //console.log(index);
            //console.log(group);

            var renderGroup = '';
            renderGroup += "<div class=\"panel panel-info\">" +
                "<div class=\"panel-heading\">" +
                "<h3 class=\"panel-title\">" + index + "</h3>" +
                "</div>" +
                "<div class=\"panel-body\">";
            var questions = group['questions'];
            $.each(questions, function (subIndex, questionLoaded) {
                var questionRendered = '';
                var placeholder;
                if (questionLoaded['placeholder']) {
                    placeholder = questionLoaded['placeholder'];
                }
                else {
                    placeholder = '';
                }
                switch (questionLoaded['type']) {
                    case "toggle":
                        questionRendered = "<div><div class=\"ui toggle checkbox\">\n" +
                            "  <input name=\"" + questionLoaded['name'] + "\" type=\"checkbox\">\n" +
                            "  <label><div>" + questionLoaded['label'] + "</div></label>" +
                            "</div><a tabindex=\"0\" role=\"button\" data-toggle=\"popover\" data-html=\"true\" title=\"" + questionLoaded['label'] + "\" data-content=\"" + questionLoaded['description'] + "\" data-trigger=\"hover\"><i class=\"glyphicon glyphicon-info-sign\"></i></a></div>";
                        renderGroup += questionRendered;
                        break;
                    case "toggle-textbox":
                        questionRendered = "<div><div class=\"ui toggle checkbox\">\n" +
                            "  <input name=\"" + questionLoaded['name'] + "\" type=\"checkbox\" onclick=\"document.getElementById(this['name']+'-textbox').disabled=!this.checked;\">" +
                            "  <label style='white-space: nowrap;display:inline'><div style='white-space: nowrap;display:inline'>" + questionLoaded['label'] + "</div></label>" +
                            "  <input type='text' id='" + questionLoaded['name'] + "-textbox' style='white-space: nowrap;display:inline' disabled placeholder='" + placeholder + "'>" +
                            "</div><a tabindex=\"0\" role=\"button\" data-toggle=\"popover\" data-html=\"true\" title=\"" + questionLoaded['label'] + "\" data-content=\"" + questionLoaded['description'] + "\" data-trigger=\"hover\" class=\"textbox-popover\"><i class=\"glyphicon glyphicon-info-sign\"></i></a></div>";
                        renderGroup += questionRendered;
                        break;
                }
            });
            renderGroup += "</div></div>";
            $("#questionnaire").append(renderGroup);
        });

    });
});

//the following function generates the tests based on the user's answers
//returns: a string containing the SHACL tests
function generateTests() {
    $.getJSON("guideline_form.json", function (loadedJson) {

    });
}

//this function run tests in an ontology.
//parameters: ontology (text data read from uploaded turtle), tests (text data from shacls to be run)
//returns: test results
function runTests(ontology, tests) {
    var validator = new SHACLValidator();
    validator.validate(ontology, "text/turtle", tests, "text/turtle", function (e, report) {
        console.log("Conforms? " + report.conforms());
        if (report.conforms() === false) {
            report.results().forEach(function (result) {
                console.log(" - Severity: " + result.severity() + " for " + result.sourceConstraintComponent());
            });
        }
    });
}