/*jshint esversion: 6 */

"use strict";

var $ = jQuery;

/* TO-DOs
* Generate full SHACL file when form is submitted
* handle ontologies inputs (uploaded and remote)
* integration with webservice (ontology and SHACL upload, loading animation after form submission
    while waiting WS response, then retrieve and list test results)
* handle textbox inputs (explode comma-separated list into several lines to substitute <$input$> in SPARQL tests)
*/


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

    $('form').on('change', ':checkbox', function () {
        console.log('checkbox ' + this.name + ' toggled');
        //checks whether the checkbox was activated or deactivated and 
        //inserts or removes the test from SHACL_selected
        if (SHACL_selected_class.has(this.name)) {
            SHACL_selected_class.delete(this.name);

        } else if (SHACL_selected_prop.has(this.name)) {
            SHACL_selected_prop.delete(this.name);
        } else {
            if (SHACL_questions_class.get(Number(this.name))) {
                SHACL_selected_class.set(this.name, SHACL_questions_class.get(Number(this.name)));
            } else {
                SHACL_selected_prop.set(this.name, SHACL_questions_prop.get(Number(this.name)));
            }
            //enable submitting after selecting at least one test
            if (document.getElementById('js-upload-submit').disabled) document.getElementById('js-upload-submit').disabled = false;
        }
        //prevent submitting without selecting tests
        let SHACL_selected = new Map(function* () {
            yield* SHACL_selected_class;
            yield* SHACL_selected_prop;
        }());
        if (SHACL_selected.size === 0) document.getElementById('js-upload-submit').disabled = true;
        console.log(SHACL_selected);
    });

    $('form').on('change, focusout', 'input[id$="-textbox"]', function (event) {
        let id = event.target.id.replace('-textbox', '');
        let query = SHACL_selected_class.get(id);
        let textInput = String(event.target.value);
        let inputArray = textInput.split(",");
        let lines = [];
        let pos = query.lastIndexOf("<$input$>");
        //finding the lines containing the placeholder <$input$>
        while (pos != -1) {
            let startLine = query.lastIndexOf("\n", pos);
            let endLine = query.indexOf("\n", pos);
            lines.push(query.substr(startLine, Number(endLine) - Number(startLine)));
            pos = query.lastIndexOf("<$input$>", startLine);
        }

        for (let [k, v] of lines.entries()) {
            v = v.repeat(inputArray.length);
            lines[k] = v;
            for (let j of inputArray) {
                lines[k] = lines[k].replace("<$input$>", j.trim());
            }
        }
        let replaceString = replaceLast(lines.join("\n"), ",", "");
        let regex = /^.*(<\$input\$>).*$/m;
        query = query.replace(regex, replaceString);
        regex = /^.*(<\$input\$>).*$/gm;
        query = query.replace(regex, "");
        
        //for(query.indexOf("<$input$>"))
        console.log(query);
    });

});

function nextTab(elem) {
    $(elem).next().find('a[data-toggle="tab"]').click();
}

function prevTab(elem) {
    $(elem).prev().find('a[data-toggle="tab"]').click();
}

/**
 * Replace last occurrence of a string with another string
 * x - the initial string
 * y - string to replace
 * z - string that will replace
 */
function replaceLast(x, y, z) {
    var a = x.split("");
    var length = y.length;
    if (x.lastIndexOf(y) != -1) {
        for (var i = x.lastIndexOf(y); i < x.lastIndexOf(y) + length; i++) {
            if (i == x.lastIndexOf(y)) {
                a[i] = z;
            } else {
                delete a[i];
            }
        }
    }

    return a.join("");
}

let ontoFile;
let shaclFile = `
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix gdl-shape: <http://dbpedia.org/gdl-shape#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .`; +
function ($) {
    // UPLOAD CLASS DEFINITION
    // ======================

    //let dropZone = document.getElementById('drop-zone');
    let uploadOntology = document.getElementById('js-ontology-submit');
    let remoteOntology = document.getElementById('js-remote-submit');
    let uploadForm = document.getElementById('js-upload-submit');

    //when the form is submitted, mount the SHACL tests file (shaclFile)
    uploadForm.addEventListener('click', function (e) {

        //let SHACL_selected = new Map(function*() { yield* SHACL_selected_class; yield* SHACL_selected_prop; }());

        //if at least one class test was selected, then insert the class shape prefixes
        if (SHACL_selected_class.size > 0) shaclFile += SHACL_prefix_class;
        //insert classes tests
        for (let [k, v] of SHACL_selected_class) {
            shaclFile += v;
        }
        shaclFile = replaceLast(shaclFile, ";", ".");
        //if at least one property test was selected, then insert the property shape prefixes
        if (SHACL_selected_prop.size > 0) shaclFile += SHACL_prefix_prop;
        //insert properties tests
        for (let [k, v] of SHACL_selected_prop) {
            shaclFile += v;
        }
        shaclFile = replaceLast(shaclFile, ";", ".");

        shaclFile = shaclFile.replace('\"', '"');
        console.log(shaclFile);

        e.preventDefault();

        let blobShacl = new Blob(Array.from(shaclFile.trim()), {
            type: 'text/turtle'
        });

        startUpload(ontoFile, blobShacl);
    });

    let startUpload = function (ontology, shacl) {
        //$("#upload-progress").show("slow");
        //let file = files[0];
        let formData = new FormData();
        formData.append("ontology", ontology);
        formData.append("shacltest", shacl);
        formData.append("format", "text/turtle");

        $.ajax({
            url: 'http://localhost:8080/ws/users/ontologyUpload',
            method: 'POST',
            type: 'POST',
            data: formData,
            accepts: { "*": "text/turtle" },
            contentType: false,
            processData: false,
            cache: false,
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

    uploadOntology.addEventListener('click', function (e) {
        ontoFile = document.getElementById('js-upload-files').files[0];
        document.getElementById('complete-step-1').disabled = false;
    });

    remoteOntology.addEventListener('click', function (e) {
        ontoFile = document.getElementById('remote-url').value;
        document.getElementById('complete-step-1').disabled = false;
    });

}(jQuery);

//array for storing the SHACL tests for actual selected questions
let SHACL_selected_class = new Map(); //SHACL_selected_class and SHACL_selected_prop
let SHACL_selected_prop = new Map();
//array for storing the SHACL tests for all questions (for the sake of reading JSON just once)
//let SHACL_questions = new Map();
let SHACL_questions_class = new Map();
let SHACL_questions_prop = new Map();
let SHACL_prefix_class;
let SHACL_prefix_prop;

//the following function generates the questionnaire HTML from JSON
jQuery(function ($) {

    function* entries(obj) {
        for (let key of Object.keys(obj)) {
            yield [key, obj[key]];
        }
    }

    let SHACL_tests_group = '';

    $.getJSON("guideline_form.json", function (loadedJson) {
        //console.log(loadedJson); // debug: output json to console
        let groups = $.parseJSON(JSON.stringify(loadedJson[0]));
        //let groups = new Map(loadedJson[0]);
        //$.each(groups, function (index, group) {
        for (let [index, group] of entries(groups)) {
            console.log(index);
            console.log(group);

            SHACL_tests_group = `
            
            gdl-shape:${groups[index].shape}
                a sh:Shape;
                `;

            //$.each(group.targetClass, function (i, shapeTargetClass) {
            //for (let shapeTargetClass in groups[index].targetClass) {
            //SHACL_tests += `sh:targetClass: ${shapeTargetClass};`;

            //check whether there is a single targetClass or multiple
            if (typeof groups[index].targetClass === 'string') {
                SHACL_tests_group += `sh:targetClass: ${groups[index].targetClass};
                `;
            } else {
                for (let i in groups[index].targetClass) {
                    SHACL_tests_group += `sh:targetClass: ${groups[index].targetClass[i]};
                    `;
                }
            }
            //}
            //});
            /*$.each(group.targetSubjectsOf, function (i, shapeTargetSubjectsOf) {
            for (let shapeTargetSubjectsOf of groups[index].targetSubjectsOf) {
                SHACL_tests += `
    sh:targetSubjectsOf: ${shapeTargetSubjectsOf};`;
            }*/
            //check whether there is a single tarSubjectsOf or multiple
            if (typeof groups[index].targetSubjectsOf === 'string') {
                SHACL_tests_group += `sh:targetSubjectsOf: ${groups[index].targetSubjectsOf};
                `;
            } else {
                for (let i in groups[index].targetSubjectsOf) {
                    SHACL_tests_group += `sh:targetSubjectsOf: ${groups[index].targetSubjectsOf[i]};
                    `;
                }
            }
            //});



            let renderGroup = '';
            renderGroup += "<div class=\"panel panel-info\">" +
                "<div class=\"panel-heading\">" +
                "<h3 class=\"panel-title\">" + index + "</h3>" +
                "</div>" +
                "<div class=\"panel-body\">";
            let questions = groups[index].questions;
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
                            "  <input name=\"" + questions[i].id + "\" type=\"checkbox\" onclick=\"document.getElementById(this['name']+'-textbox').disabled=!this.checked;document.getElementById(this['name']+'-textbox').value='';\">" +
                            "  <label style='white-space: nowrap;display:inline'><div style='white-space: nowrap;display:inline'>" + questions[i].label + "</div></label>" +
                            "  <input type='text' id='" + questions[i].id + "-textbox' style='white-space: nowrap;display:inline' disabled placeholder='" + placeholder + "'>" +
                            "</div><a tabindex=\"0\" role=\"button\" data-toggle=\"popover\" data-html=\"true\" title=\"" + questions[i].label + "\" data-content=\"" + questions[i].description + "\" data-trigger=\"hover\" class=\"textbox-popover\"><i class=\"glyphicon glyphicon-info-sign\"></i></a></div>";
                        renderGroup += questionRendered;
                        break;
                }
                let thisSHACL = `${questions[i].shacl} [
        sh:message: "${questions[i].label}";
        `;
                switch (questions[i].shacl) {
                    case "sh:sparql":
                        thisSHACL += `sh:select """
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            ${questions[i].test.join('\n')}
            """;
      ];
      
      `;
                        break;
                    case "sh:property":
                        let prop = questions[i].test.join('\n');
                        thisSHACL += `${prop}
                            ];
                            
                            `;
                        break;
                }
                switch (index) {
                    case "Classes":
                        SHACL_questions_class.set(questions[i].id, thisSHACL);
                        SHACL_prefix_class = SHACL_tests_group;
                        break;
                    case "Properties":
                        SHACL_questions_prop.set(questions[i].id, thisSHACL);
                        SHACL_prefix_prop = SHACL_tests_group;
                        break;
                }


                //});
            }
            renderGroup += "</div></div>";
            $("#questionnaire").append(renderGroup);
            //});
            //SHACL_tests += SHACL_tests_group;

        }
        //console.log(SHACL_questions);


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