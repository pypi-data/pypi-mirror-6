
jQuery(function($) {
    $(document).ready( function() {
        // configure the report options to be an overlay
        var dialogContent = $("#options-dialog").html();
        $("#options-dialog").addClass("overlay overlay-ajax").html(
            '<div class="close"></div><div class="pb-ajax"><div><div>'
            + '</div></div></div>'
        );
        $("#options-dialog .pb-ajax div div").html(dialogContent);

        // define the options dialog overlay
        $(".documentFirstHeading > a").overlay();


        // provide select all functionality for the document types
        $("h3.docTypes").append(
            '<a href="" class="selectAll" rel="all">unselect all</a>'
        );
        $("h3.docTypes a.selectAll").click( function(e) {
            e.preventDefault();
            if ($(this).text() == "unselect all") {
                // unselect all
                $("ul.docTypes input").removeAttr("checked");
                $(this).text("select all");

            } else {
                // select all
                $("ul.docTypes input").attr("checked", "checked");
                $(this).text("unselect all");
            }
        });

        // determine the initial state of the select all link
        $("ul.docTypes input").each( function() {
            if ($(this).attr("checked") != "checked" &&
                $(this).attr("checked") != true
            ) {
                $("h3.docTypes a.selectAll").text("select all");
                return;
            }
        });
    });
});