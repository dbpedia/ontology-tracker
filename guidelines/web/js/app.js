/*jshint esversion: 6 */

"use strict";

var $ = jQuery;

$(document).ready(function () {
    //Initialize popover
    $("body").popover({
        selector: '[data-toggle=popover]'
    });
    //Initialize tooltips
    $('.nav-tabs > li a[title]').tooltip();
    $('.col-xs-2 > a[title]').tooltip();

    //Initialize wizard navigation bar
    $('a[data-toggle="tab"]').on('show.bs.tab', function (e) {

        let $target = $(e.target);

        if ($target.parent().hasClass('disabled')) {
            return false;
        }
    });

    $(".next-step").click(function (e) {

        let $active = $('.wizard .nav-tabs li.active');
        $active.next().removeClass('disabled');
        nextTab($active);

    });
    $(".prev-step").click(function (e) {

        let $active = $('.wizard .nav-tabs li.active');
        prevTab($active);

    });

    $('form').on('change', ':checkbox', function(){
            console.log('checkbox ' + this.name + ' toggled');
            //checks whether the checkbox was activated or deactivated and 
            //inserts or removes the test from SHACL_selected
            if(SHACL_selected.has(this.name)) {
                SHACL_selected.delete(this.name);
            }
            else {
                SHACL_selected.set(this.name, SHACL_questions.get(Number(this.name)));
            }
            console.log(SHACL_selected);
        });
   // }

});

function nextTab(elem) {
    $(elem).next().find('a[data-toggle="tab"]').click();
}

function prevTab(elem) {
    $(elem).prev().find('a[data-toggle="tab"]').click();
}

+
function ($) {
    'use strict';

    // UPLOAD CLASS DEFINITION
    // ======================

    let dropZone = document.getElementById('drop-zone');
    let uploadForm = document.getElementById('js-upload-form');

    let startUpload = function (file) {
        $("#upload-progress").show("slow");
        //let file = files[0];
        let formData = new FormData();
        formData.append("file1", file);

        $.ajax({
            url: 'http://localhost:8080/ws/ontology',
            method: 'POST',
            type: 'POST',
            data: formData,
            contentType: 'text/turtle',
            processData: false,
            xhr: function () {
                let xhr = new window.XMLHttpRequest();
                xhr.upload.addEventListener("progress",
                    uploadProgressHandler,
                    false
                );
                xhr.addEventListener("load", loadHandler, false);
                xhr.addEventListener("error", errorHandler, false);
                //xhr.addEventListener("abort", abortHandler, false);

                return xhr;
            }
        });

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
        let percent = (event.loaded / event.total) * 100;
        let progress = Math.round(percent);
        $(".progress-bar").attr('aria-value-now', progress.toString());
        $(".progress-bar").attr('style', 'width: ' + progress.toString() + '%');
        $(".sr-only").html(progress + "% Complete");
    }

    uploadForm.addEventListener('submit', function (e) {
        let uploadFile = document.getElementById('js-upload-files').files[0];
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

let SHACL_tests = `
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix dbo-shape: <http://dbpedia.org/dbo-shape#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

`;

//array for storing the SHACL tests for actual selected questions
let SHACL_selected = new Map();
//array for storing the SHACL tests for all questions (for the sake of reading JSON just once)
let SHACL_questions = new Map();

//the following function generates the questionnaire HTML from JSON
jQuery(function ($) {




    $.getJSON("guideline_form.json", function (loadedJson) {
        //console.log(loadedJson); // debug: output json to console
        let groups = $.parseJSON(JSON.stringify(loadedJson[0]));
        //$.each(groups, function (index, group) {
        for (var group in groups) {
            //console.log(index);
            //console.log(group);

            SHACL_tests += `dbo-shape: ${groups[group].shape}
                a sh:Shape;`;

            //$.each(group.targetClass, function (i, shapeTargetClass) {
            for (var shapeTargetClass in groups[group].targetClass) {
                SHACL_tests += `sh:targetClass: ${shapeTargetClass};`;
            }
            //});
            //$.each(group.targetSubjectsOf, function (i, shapeTargetSubjectsOf) {
            for (var shapeTargetSubjectsOf in groups[group].targetSubjectsOf) {
                SHACL_tests += `
    sh:targetSubjectsOf: ${shapeTargetSubjectsOf};`;
            }
            //});



            let renderGroup = '';
            renderGroup += "<div class=\"panel panel-info\">" +
                "<div class=\"panel-heading\">" +
                "<h3 class=\"panel-title\">" + group + "</h3>" +
                "</div>" +
                "<div class=\"panel-body\">";
            let questions = groups[group].questions;
            // $.each(questions, function (subIndex, questionLoaded) {
            //for(var questionLoaded in questions) {
            for (var i in questions) {
                let questionRendered = '';
                let placeholder;
                if (questions[i].placeholder) {
                    placeholder = questions[i].placeholder;
                } else {
                    placeholder = '';
                }
                switch (questions[i].type) {
                    case "toggle":
                        questionRendered = "<div><div class=\"ui toggle checkbox\">\n" +
                            "  <input name=\"" + questions[i].id + "\" type=\"checkbox\">\n" +
                            "  <label><div>" + questions[i].label + "</div></label>" +
                            "</div><a tabindex=\"0\" role=\"button\" data-toggle=\"popover\" data-html=\"true\" title=\"" + questions[i].label + "\" data-content=\"" + questions[i].description + "\" data-trigger=\"hover\"><i class=\"glyphicon glyphicon-info-sign\"></i></a></div>";
                        renderGroup += questionRendered;
                        break;
                    case "toggle-textbox":
                        questionRendered = "<div><div class=\"ui toggle checkbox\">\n" +
                            "  <input name=\"" + questions[i].id + "\" type=\"checkbox\" onclick=\"document.getElementById(this['name']+'-textbox').disabled=!this.checked;\">" +
                            "  <label style='white-space: nowrap;display:inline'><div style='white-space: nowrap;display:inline'>" + questions[i].label + "</div></label>" +
                            "  <input type='text' id='" + questions[i].id + "-textbox' style='white-space: nowrap;display:inline' disabled placeholder='" + placeholder + "'>" +
                            "</div><a tabindex=\"0\" role=\"button\" data-toggle=\"popover\" data-html=\"true\" title=\"" + questions[i].label + "\" data-content=\"" + questions[i].description + "\" data-trigger=\"hover\" class=\"textbox-popover\"><i class=\"glyphicon glyphicon-info-sign\"></i></a></div>";
                        renderGroup += questionRendered;
                        break;
                }
                let thisSHACL = `${questions[i].shacl} [
        sh:message ${questions[i].label}";
        `;
                switch (questions[i].shacl) {
                    case "sh:sparql":
                        thisSHACL += `sh:select """
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            ${questions[i].test}
            """;
      ];`;
                        break;
                    case "sh:property":
                        thisSHACL += `${questions[i].test}
                            ];`;
                        break;
                }
                SHACL_questions.set(questions[i].id, thisSHACL);


                //});
            }
            renderGroup += "</div></div>";
            $("#questionnaire").append(renderGroup);
            //});
        }
        console.log(SHACL_questions);
    });



    /*uploadForm.addEventListener('onclick', function (e) {
        let uploadFile = document.getElementById('js-upload-files').files[0];
        e.preventDefault()

        startUpload(uploadFile)
    });*/
});


/*the following function generates the tests based on the user's answers
//returns: a string containing the SHACL tests
function generateTests() {
    $.getJSON("guideline_form.json", function (loadedJson) {

    });
}

//this function run tests in an ontology.
//parameters: ontology (text data read from uploaded turtle), tests (text data from shacls to be run)
//returns: test results
function runTests(ontology, tests) {
    let validator = new SHACLValidator();
    validator.validate(ontology, "text/turtle", tests, "text/turtle", function (e, report) {
        console.log("Conforms? " + report.conforms());
        if (report.conforms() === false) {
            report.results().forEach(function (result) {
                console.log(" - Severity: " + result.severity() + " for " + result.sourceConstraintComponent());
            });
        }
    });
}*/