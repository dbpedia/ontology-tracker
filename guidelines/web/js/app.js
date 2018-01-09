/*jshint esversion: 6 */

"use strict";

var $ = jQuery;

/* TO-DOs
 * handle ontology remote input
 * integration with webservice (list test results)
 */


$(document).ready(function () {
    //Initialize popover
    $("body").popover({
        selector: '[data-toggle=popover]'
    });
    //Initialize tooltips
    $('.nav-tabs > li a[title]').tooltip();
    $('.col-xs-2 > a[title]').tooltip();

    $('#list-success').collapse({
        toggle: false
    });
    $('#list-warning').collapse({
        toggle: false
    });
    $('#list-error').collapse({
        toggle: false
    });

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

    $('#complete-step-1').prop("disabled", true);

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

        console.log(query);
        SHACL_selected_class.set(id, query);
    });

});

function nextTab(elem) {
    $(elem).next().find('a[data-toggle="tab"]').click();
}

function prevTab(elem) {
    $(elem).prev().find('a[data-toggle="tab"]').click();
}

let error = [];
let error2 = new Map();

function listTestResults(res) {

    let sev, msg, resource; //severity, message and resource
    for (let i of res) {
        let testResults = [];
        let test1 = [];
        msg = i.message.trim();
        resource = i.failingresource.trim();
        if (!error2.has(msg)) {
            test1.push(resource);
            error2.set(msg, test1);
        } else {
            test1 = error2.get(msg);
            test1.push(resource);
            error2.set(msg, test1);
        }
        for (let k of i.propertyValuePairs) {
            if (k.property == "http://www.w3.org/ns/shacl#resultSeverity") {
                sev = k.values[0];
                break;
            } else continue;
        }
        testResults.push(msg);
        testResults.push(sev);
        testResults.push(resource);
        if (sev == "http://www.w3.org/ns/shacl#Violation") error.push(testResults);
        //else if (sev == "http://www.w3.org/ns/shacl#Warning") warning.push(testResults);
        //else info.push(testResults);
        // ps: at the moment, RDFUnit has only "Violation" results
    }
    //$("#num-success").html(info.length + " tests passed");
    //$("#num-warning").html(warning.length + " tests has warnings");
    $("#num-error").html(error2.size + " tests failed, " + error.length + " violations");

    let errorHtml = `<ul>
    `;
    for (let i of error) {
        errorHtml += `<div class="list-group-item list-group-item-danger">
            <div class="col-sm-8">` + i[0].replace("<", "").replace(">", "").replace("\\", "") + `</div>
            <div class="col-sm-4"><a href="` + i[2] + `">` + i[2] + `</a></div>
        </div>
        `;

    }
    errorHtml += `
    </ul>`;
    $("#list-error").html(errorHtml);
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
let shaclFile = `@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
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


        $(".lds-spinner").show();

        shaclFile += `
        gdl-shape:
          rdfs:label "SHACL for Ontology Guidelines"@en ;
          rdfs:comment "This graph is used to validate ontologies against pre-selected tests. "@en ;
          sh:declare [
              sh:prefix "rdfs" ;
              sh:namespace "http://www.w3.org/2000/01/rdf-schema#"^^xsd:anyURI ;
          ] ;
          sh:declare [
              sh:prefix "owl" ;
              sh:namespace "http://www.w3.org/2002/07/owl#"^^xsd:anyURI ;
          ] ;
          sh:declare [
              sh:prefix "rdf" ;
              sh:namespace "http://www.w3.org/1999/02/22-rdf-syntax-ns#"^^xsd:anyURI ;
          ] ;
          sh:declare [
              sh:prefix "gdl" ;
              sh:namespace "http://dbpedia.org/ontology-guidelines/"^^xsd:anyURI ;
        ] .
        
        `;

        //if at least one class test was selected, then insert the class shape prefixes
        if (SHACL_selected_class.size > 0) {
            shaclFile += SHACL_prefix_class;
            //insert classes tests
            for (let [k, v] of SHACL_selected_class) {
                shaclFile += v;
            }
            shaclFile = replaceLast(shaclFile, ";", " .");
        }
        //if at least one property test was selected, then insert the property shape prefixes
        if (SHACL_selected_prop.size > 0) {
            shaclFile += SHACL_prefix_prop;
            //insert properties tests
            for (let [k, v] of SHACL_selected_prop) {
                shaclFile += v;
            }
            shaclFile = replaceLast(shaclFile, ";", " .");
        }

        shaclFile = shaclFile.replace('\"', '"');
        console.log(shaclFile);

        e.preventDefault();

        let blobShacl = new Blob(Array.from(shaclFile.trim()), {
            type: 'text/turtle'
        });

        startUpload(ontoFile, blobShacl);
    });

    let startUpload = function (ontology, shacl) {
        let formData = new FormData();
        formData.append("ontology", ontology);
        formData.append("shacltest", shacl);
        formData.append("format", "text/turtle");

        $.ajax({
            data: formData,
            url: 'http://localhost:8081/ws/users/ontologyUpload',
            method: 'POST',
            type: 'POST',
            accepts: {
                "*": "text/turtle"
            },
            contentType: false,
            processData: false,
            cache: false,
            async: false,
            success: function (r) {
                // console.dir(r);
                //$("#results").append(r);
                if (r) {
                    var response = JSON.parse(r);
                    console.log(response);
                    listTestResults(response);
                } else {
                    $("#num-error").html("0 tests failed, 0 violations");
                }
            },
            xhr: function () {
                let xhr = new window.XMLHttpRequest();
                return xhr;
            }
        }).complete(function () {
            $(".lds-spinner").hide();
        });
        /*request.fail(function(jqXHR, textStatus) {
            console.log( "Request failed: " + textStatus );
        });*/
    };

    uploadOntology.addEventListener('click', function (e) {
        ontoFile = document.getElementById('js-upload-files').files[0];
        document.getElementById('complete-step-1').disabled = false;
    });

    remoteOntology.addEventListener('click', function (e) {
        ontoFile = document.getElementById('remote-url').value;
        document.getElementById('complete-step-1').disabled = false;
    });

}(jQuery);

//arrays for storing the SHACL tests for actual selected questions
let SHACL_selected_class = new Map();
let SHACL_selected_prop = new Map();
//arrays for storing the SHACL tests for all questions
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
        console.log(loadedJson); // debug: output json to console
        let groups = $.parseJSON(JSON.stringify(loadedJson[0]));

        for (let [index, group] of entries(groups)) {
            console.log(index);
            console.log(group);

            SHACL_tests_group = `
            
            gdl-shape:${groups[index].shape}
                a sh:Shape;
                `;

            //check whether there is a single or multiple targetClass
            if (typeof groups[index].targetClass === 'string') {
                SHACL_tests_group += `sh:targetClass ${groups[index].targetClass};
                `;
            } else {
                for (let i in groups[index].targetClass) {
                    SHACL_tests_group += `sh:targetClass ${groups[index].targetClass[i]};
                    `;
                }
            }

            //check whether there is a single or multiple targetSubjectsOf 
            if (typeof groups[index].targetSubjectsOf === 'string') {
                SHACL_tests_group += `sh:targetSubjectsOf ${groups[index].targetSubjectsOf};
                `;
            } else {
                for (let i in groups[index].targetSubjectsOf) {
                    SHACL_tests_group += `sh:targetSubjectsOf ${groups[index].targetSubjectsOf[i]};
                    `;
                }
            }

            let renderGroup = '';
            renderGroup += "<div class=\"panel panel-info\">" +
                "<div class=\"panel-heading\">" +
                "<h3 class=\"panel-title\">" + index + "</h3>" +
                "</div>" +
                "<div class=\"panel-body\">";

            let questions = groups[index].questions;

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
        sh:message "${questions[i].label}";
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
                        thisSHACL += replaceLast(prop, '.', ';');
                        thisSHACL += ` ];
                            
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

            }
            renderGroup += "</div></div>";
            $("#questionnaire").append(renderGroup);

        }

    });


});